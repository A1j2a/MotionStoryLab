"use client";

import { useState, useEffect, useRef } from "react";
import {
  X,
  Copy,
  Check,
  Sparkles,
  UploadCloud,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Video,
  Music,
  FileVideo,
  RefreshCw,
  Clock,
  ExternalLink,
} from "lucide-react";
import { api } from "@/lib/api";
import { Scene } from "@/lib/types";

interface SceneVideoModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  scene: (Scene & { uploaded_file?: string | null; uploaded_duration?: number | null; prompt_status?: string | null }) | null;
  onSceneUpdated?: (updatedScene: any) => void;
}

interface MatchCandidate {
  filename: string;
  tmp_path: string;
  confidence: number;
  reason: string;
  source: string;
  is_current: boolean;
}

export default function SceneVideoModal({
  isOpen,
  onClose,
  projectId,
  scene,
  onSceneUpdated,
}: SceneVideoModalProps) {
  const [currentScene, setCurrentScene] = useState(scene);
  const [videoTimestamp, setVideoTimestamp] = useState<number>(Date.now());
  const [videoError, setVideoError] = useState(false);
  const [copiedPrompt, setCopiedPrompt] = useState(false);
  const [copiedFilename, setCopiedFilename] = useState(false);

  // AI Reassign State
  const [reassigning, setReassigning] = useState(false);
  const [reassignResult, setReassignResult] = useState<{
    success: boolean;
    confidence?: number;
    reason?: string;
    source?: string;
    reassigned?: boolean;
    assigned_file?: string | null;
  } | null>(null);
  const [candidates, setCandidates] = useState<MatchCandidate[]>([]);
  const [assigningCandidate, setAssigningCandidate] = useState<string | null>(null);

  // Direct Upload State
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setCurrentScene(scene);
    setVideoTimestamp(Date.now());
    setVideoError(false);
    setReassignResult(null);
    setCandidates([]);
  }, [scene]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !currentScene) return null;

  const hasFile = !!currentScene.uploaded_file;
  const fileName = currentScene.uploaded_file
    ? currentScene.uploaded_file.split("/").pop()
    : null;
  const duration = currentScene.uploaded_duration || currentScene.duration || 0;
  const videoUrl = `${api.getSceneVideoUrl(projectId, currentScene.id)}?t=${videoTimestamp}`;

  const handleCopyPrompt = async () => {
    const text =
      currentScene.video_prompt ||
      currentScene.dialogue ||
      currentScene.lyrics ||
      "";
    if (!text) return;
    await navigator.clipboard.writeText(text);
    setCopiedPrompt(true);
    setTimeout(() => setCopiedPrompt(false), 2000);
  };

  const handleCopyFilename = async () => {
    if (!fileName) return;
    await navigator.clipboard.writeText(fileName);
    setCopiedFilename(true);
    setTimeout(() => setCopiedFilename(false), 2000);
  };

  // Re-check & Match with AI
  const handleAiReassign = async () => {
    if (!currentScene) return;
    setReassigning(true);
    setReassignResult(null);
    try {
      const res = await api.aiReassignSceneVideo(projectId, currentScene.id, {
        apply_match: true,
      });

      setReassignResult({
        success: true,
        confidence: res.confidence,
        reason: res.match_reason,
        source: res.match_source,
        reassigned: res.reassigned,
        assigned_file: res.assigned_file,
      });

      if (res.candidates) {
        setCandidates(res.candidates);
      }

      if (res.scene) {
        const updated = {
          ...currentScene,
          uploaded_file: res.scene.uploaded_file,
          uploaded_duration: res.scene.uploaded_duration,
          prompt_status: "VIDEO_UPLOADED",
        };
        setCurrentScene(updated);
        setVideoTimestamp(Date.now());
        setVideoError(false);
        if (onSceneUpdated) {
          onSceneUpdated(updated);
        }
      }
    } catch (err: any) {
      setReassignResult({
        success: false,
        reason: err?.message || "AI Matching failed. Please ensure video files exist.",
      });
    } finally {
      setReassigning(false);
    }
  };

  // Assign specific candidate
  const handleAssignCandidate = async (cand: MatchCandidate) => {
    if (!currentScene) return;
    setAssigningCandidate(cand.tmp_path);
    try {
      const res = await api.aiReassignSceneVideo(projectId, currentScene.id, {
        apply_match: true,
        candidate_tmp_path: cand.tmp_path,
      });

      setReassignResult({
        success: true,
        confidence: res.confidence,
        reason: res.match_reason,
        reassigned: true,
        assigned_file: res.assigned_file,
      });

      if (res.scene) {
        const updated = {
          ...currentScene,
          uploaded_file: res.scene.uploaded_file,
          uploaded_duration: res.scene.uploaded_duration,
          prompt_status: "VIDEO_UPLOADED",
        };
        setCurrentScene(updated);
        setVideoTimestamp(Date.now());
        setVideoError(false);
        if (onSceneUpdated) {
          onSceneUpdated(updated);
        }
      }
    } catch (err: any) {
      alert("Candidate assignment failed: " + (err?.message || err));
    } finally {
      setAssigningCandidate(null);
    }
  };

  // Direct File Upload to this Slot
  const handleDirectUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !currentScene) return;
    setUploading(true);
    try {
      const res = await api.uploadSceneVideo(projectId, currentScene.id, file, true);
      const updated = {
        ...currentScene,
        uploaded_file: res.uploaded_file,
        uploaded_duration: res.uploaded_duration,
        prompt_status: "VIDEO_UPLOADED",
      };
      setCurrentScene(updated);
      setVideoTimestamp(Date.now());
      setVideoError(false);
      setReassignResult({
        success: true,
        confidence: 100,
        reason: `Directly uploaded and assigned: ${res.uploaded_filename || file.name}`,
        assigned_file: res.uploaded_filename || file.name,
      });
      if (onSceneUpdated) {
        onSceneUpdated(updated);
      }
    } catch (err: any) {
      alert("Video upload failed: " + (err?.message || err));
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="relative w-full max-w-4xl bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[92vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/70">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center shadow-xs">
              <Video className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-black text-slate-900 tracking-tight">
                  Scene {String(currentScene.scene_number).padStart(2, "0")} Slot
                </h3>
                {hasFile ? (
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-black bg-emerald-100 text-emerald-800 border border-emerald-300">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                    <span>Assigned ({duration.toFixed(1)}s)</span>
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-black bg-amber-100 text-amber-800 border border-amber-300">
                    <AlertCircle className="w-3 h-3 text-amber-600" />
                    <span>Vacant Slot</span>
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 font-medium mt-0.5">
                {hasFile
                  ? `File: ${fileName}`
                  : "No video clip assigned yet • Click Reassign with AI or upload a clip"}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-slate-200/70 hover:bg-slate-200 text-slate-600 hover:text-slate-900 flex items-center justify-center transition-all cursor-pointer"
            title="Close modal"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column: Video Player Preview (7 cols) */}
            <div className="lg:col-span-7 space-y-3">
              <div className="aspect-video bg-black rounded-2xl overflow-hidden shadow-md relative flex items-center justify-center border border-slate-800">
                {hasFile && !videoError ? (
                  <video
                    key={`slot-video-${currentScene.id}-${videoTimestamp}`}
                    src={videoUrl}
                    controls
                    autoPlay
                    playsInline
                    onError={() => setVideoError(true)}
                    className="w-full h-full object-contain"
                  />
                ) : hasFile && videoError ? (
                  <div className="p-6 text-center text-white space-y-2">
                    <AlertCircle className="w-8 h-8 text-amber-400 mx-auto" />
                    <p className="text-xs font-bold">Video stream loading or format error</p>
                    <p className="text-[11px] text-slate-400 font-mono truncate max-w-xs mx-auto">
                      {fileName}
                    </p>
                    <button
                      onClick={() => {
                        setVideoError(false);
                        setVideoTimestamp(Date.now());
                      }}
                      className="px-3 py-1 bg-white/10 hover:bg-white/20 text-white rounded-lg text-xs font-semibold inline-flex items-center gap-1.5 transition-colors cursor-pointer"
                    >
                      <RefreshCw className="w-3 h-3" />
                      <span>Retry Playback</span>
                    </button>
                  </div>
                ) : (
                  <div className="p-8 text-center text-slate-400 space-y-3">
                    <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mx-auto text-amber-400">
                      <FileVideo className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-white">No Video Assigned</p>
                      <p className="text-xs text-slate-400 mt-1 max-w-xs">
                        This slot is vacant. Use &ldquo;Reassign with AI&rdquo; to match an uploaded clip, or upload a video file below.
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Video metadata bar */}
              <div className="flex flex-wrap items-center justify-between gap-2 p-3 bg-slate-50 border border-slate-200/80 rounded-xl text-xs">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="font-bold text-slate-700 shrink-0">Assigned Clip:</span>
                  <span
                    className="font-mono text-slate-600 truncate max-w-[200px] sm:max-w-[260px]"
                    title={fileName || "Vacant"}
                  >
                    {fileName || "None (Vacant)"}
                  </span>
                  {fileName && (
                    <button
                      onClick={handleCopyFilename}
                      className="p-1 text-slate-400 hover:text-slate-700 transition-colors"
                      title="Copy filename"
                    >
                      {copiedFilename ? (
                        <Check className="w-3.5 h-3.5 text-emerald-600" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                  )}
                </div>

                <div className="flex items-center gap-2 text-slate-500 font-medium">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Duration: {duration.toFixed(1)}s</span>
                </div>
              </div>
            </div>

            {/* Right Column: Prompt & AI Reassign Controls (5 cols) */}
            <div className="lg:col-span-5 space-y-4">
              {/* Scene Prompt Card */}
              <div className="p-4 bg-orange-50/60 border border-orange-200 rounded-2xl space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-black uppercase tracking-wider text-orange-900 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-[#FF6B00]" />
                    <span>Slot Visual Prompt</span>
                  </span>
                  <button
                    onClick={handleCopyPrompt}
                    className="inline-flex items-center gap-1 text-[11px] font-bold text-orange-700 hover:text-orange-950 px-2 py-0.5 rounded-lg bg-orange-100/70 hover:bg-orange-200 transition-colors cursor-pointer"
                  >
                    {copiedPrompt ? (
                      <>
                        <Check className="w-3 h-3 text-emerald-600" />
                        <span>Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                </div>
                <p className="text-xs text-slate-700 leading-relaxed max-h-36 overflow-y-auto pr-1">
                  {currentScene.video_prompt ||
                    currentScene.dialogue ||
                    "No visual prompt set for this scene."}
                </p>
              </div>

              {/* Song Lyrics / Audio Card */}
              {currentScene.lyrics && (
                <div className="p-3 bg-indigo-50/60 border border-indigo-200/80 rounded-2xl space-y-1">
                  <span className="text-[10px] font-black uppercase tracking-wider text-indigo-900 flex items-center gap-1.5">
                    <Music className="w-3 h-3 text-indigo-600" />
                    <span>Song Lyrics (Audio Timing)</span>
                  </span>
                  <p className="text-xs text-indigo-950 font-medium italic">
                    &ldquo;{currentScene.lyrics}&rdquo;
                  </p>
                </div>
              )}

              {/* AI Reassign & Match Action Buttons */}
              <div className="space-y-2 pt-1">
                <button
                  type="button"
                  onClick={handleAiReassign}
                  disabled={reassigning || uploading}
                  className="w-full py-3 px-4 bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-600 hover:opacity-95 text-white rounded-2xl text-xs font-bold transition-all shadow-md shadow-indigo-500/20 flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  {reassigning ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Checking with AI & Matching Video…</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 text-amber-300" />
                      <span>Reassign with AI (Match Video to Prompt)</span>
                    </>
                  )}
                </button>

                <div className="flex items-center gap-2">
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleDirectUpload}
                    accept="video/mp4,video/quicktime,video/webm"
                    className="hidden"
                  />
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploading || reassigning}
                    className="w-full py-2.5 px-3 bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-50"
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="w-3.5 h-3.5 animate-spin text-[#FF6B00]" />
                        <span>Uploading Clip…</span>
                      </>
                    ) : (
                      <>
                        <UploadCloud className="w-3.5 h-3.5 text-[#FF6B00]" />
                        <span>Replace / Upload New Clip for Scene</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* AI Match Result Banner */}
              {reassignResult && (
                <div
                  className={`p-3.5 rounded-2xl border text-xs space-y-1.5 transition-all ${
                    reassignResult.success
                      ? "bg-emerald-50/90 border-emerald-300 text-emerald-950"
                      : "bg-red-50/90 border-red-200 text-red-900"
                  }`}
                >
                  <div className="flex items-center justify-between font-bold">
                    <span className="flex items-center gap-1.5">
                      {reassignResult.success ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-red-500" />
                      )}
                      <span>
                        {reassignResult.reassigned
                          ? "AI Successfully Reassigned Clip!"
                          : reassignResult.success
                          ? "AI Match Verified"
                          : "AI Matching Issue"}
                      </span>
                    </span>
                    {reassignResult.confidence !== undefined && (
                      <span className="px-2 py-0.5 rounded-md bg-emerald-200/80 text-emerald-900 font-extrabold text-[10px]">
                        {reassignResult.confidence.toFixed(0)}% Match
                      </span>
                    )}
                  </div>
                  {reassignResult.reason && (
                    <p className="text-[11px] leading-relaxed text-slate-700">
                      {reassignResult.reason}
                    </p>
                  )}
                  {reassignResult.assigned_file && (
                    <p className="text-[10px] font-mono font-semibold text-emerald-800">
                      Assigned: {reassignResult.assigned_file}
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Alternative Candidates Section */}
          {candidates.length > 0 && (
            <div className="pt-4 border-t border-slate-200 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-black text-slate-900 flex items-center gap-1.5">
                  <FileVideo className="w-4 h-4 text-indigo-600" />
                  <span>Available Candidate Video Clips for this Slot ({candidates.length})</span>
                </span>
                <span className="text-[11px] text-slate-500">
                  Select any clip to manually switch or re-link
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {candidates.map((cand) => (
                  <div
                    key={cand.tmp_path}
                    className={`p-3 rounded-xl border flex items-center justify-between gap-3 transition-all ${
                      cand.is_current
                        ? "bg-indigo-50/70 border-indigo-300 ring-1 ring-indigo-400"
                        : "bg-slate-50 hover:bg-white border-slate-200"
                    }`}
                  >
                    <div className="min-w-0 space-y-0.5">
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono font-bold text-xs text-slate-800 truncate" title={cand.filename}>
                          {cand.filename}
                        </span>
                        {cand.is_current && (
                          <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-indigo-200 text-indigo-900">
                            Current
                          </span>
                        )}
                      </div>
                      <p className="text-[10px] text-slate-500 line-clamp-1">
                        {cand.reason}
                      </p>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <span className="text-[10px] font-extrabold px-1.5 py-0.5 rounded bg-slate-200 text-slate-700">
                        {cand.confidence.toFixed(0)}%
                      </span>
                      {!cand.is_current && (
                        <button
                          type="button"
                          onClick={() => handleAssignCandidate(cand)}
                          disabled={assigningCandidate === cand.tmp_path}
                          className="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-[10px] font-bold transition-all cursor-pointer disabled:opacity-50 flex items-center gap-1"
                        >
                          {assigningCandidate === cand.tmp_path ? (
                            <Loader2 className="w-3 h-3 animate-spin" />
                          ) : (
                            <span>Assign</span>
                          )}
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between px-6 py-3.5 bg-slate-50 border-t border-slate-100 text-xs">
          <span className="text-slate-500">
            Click on any scene slot anytime to preview the assigned video and prompt.
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold transition-colors cursor-pointer"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
