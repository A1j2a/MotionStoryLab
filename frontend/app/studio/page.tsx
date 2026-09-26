"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { Project, Scene } from "@/lib/types";
import {
  CheckCircle2,
  Circle,
  Copy,
  Check,
  Film,
  Upload,
  Clapperboard,
  Music,
  Video,
  Play,
  Loader2,
  RefreshCw,
  AlertTriangle,
  ChevronRight,
  ChevronDown,
  UploadCloud,
  X,
  ExternalLink,
  Clock,
  Layers,
  Sparkles,
  ArrowRight,
  FileVideo,
  ListOrdered,
  Zap,
} from "lucide-react";

type PromptStatus = "NOT_COPIED" | "PROMPT_COPIED" | "VIDEO_UPLOADED" | "ORDER_CONFIRMED" | "FAILED";

interface SceneWithStatus extends Scene {
  prompt_status: PromptStatus;
  prompt_copied_at?: string | null;
  uploaded_file?: string | null;
  uploaded_duration?: number | null;
  scene_order?: number;
}

interface UploadResult {
  filename: string;
  status: "UPLOADED" | "NEEDS_ASSIGNMENT" | "REJECTED";
  scene_number?: number;
  duration?: number;
  tmp_path?: string;
  reason?: string;
}

interface UnresolvedFile {
  filename: string;
  tmp_path: string;
  duration?: number;
  suggested_scene_number?: number;
  confidence?: number;
  match_reason?: string;
  match_source?: string;
}

interface AssemblyReadiness {
  ready: boolean;
  total_scenes: number;
  uploaded_scenes: number;
  missing_scenes: number[];
  audio_available: boolean;
  srt_available: boolean;
  sequence_confirmed: boolean;
}

const STEPS = [
  { id: 1, label: "Topic & SEO" },
  { id: 2, label: "Song" },
  { id: 3, label: "SRT" },
  { id: 4, label: "Scene Prompts" },
  { id: 5, label: "Copy & Track" },
  { id: 6, label: "Upload Scenes" },
  { id: 7, label: "Verify Order" },
  { id: 8, label: "Final Video" },
];

function ScenePromptCard({
  scene,
  onCopied,
}: {
  scene: SceneWithStatus;
  onCopied: (sceneId: string) => void;
}) {
  const [justCopied, setJustCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const isCopied = scene.prompt_status && scene.prompt_status !== "NOT_COPIED";
  const promptText = scene.video_prompt || scene.dialogue || `Scene ${scene.scene_number}: ${scene.lyrics || ""}`;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(promptText);
    setJustCopied(true);
    onCopied(scene.id);
    setTimeout(() => setJustCopied(false), 2000);
  };

  const formatTime = (secs?: number | null) => {
    if (!secs && secs !== 0) return "--:--";
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  return (
    <div className={`border rounded-2xl transition-all ${isCopied ? "border-green-300 bg-green-50/40" : "border-[#E5E5EA] bg-white"}`}>
      <div className="flex items-center justify-between p-4 gap-3">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <div className={`w-3 h-3 rounded-full flex-shrink-0 ${scene.prompt_status === "ORDER_CONFIRMED" ? "bg-blue-500" : scene.prompt_status === "VIDEO_UPLOADED" ? "bg-purple-500" : isCopied ? "bg-green-500" : "bg-[#C7C7CC]"}`} />
          <span className="font-bold text-[#1D1D1F] text-sm">Scene {String(scene.scene_number).padStart(2, "0")}</span>
          <span className="text-[#86868B] text-xs flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {formatTime(scene.start_time)} – {formatTime(scene.end_time)} ({scene.duration?.toFixed(1)}s)
          </span>
          {scene.lyrics && <span className="text-[#1D1D1F] text-xs italic truncate max-w-48">"{scene.lyrics}"</span>}
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {scene.prompt_status === "VIDEO_UPLOADED" && <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full font-medium">✓ Video Uploaded</span>}
          {scene.prompt_status === "PROMPT_COPIED" && <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">✓ Prompt Copied</span>}
          {(!scene.prompt_status || scene.prompt_status === "NOT_COPIED") && <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full font-medium">Not Copied</span>}
          <button onClick={() => setExpanded(!expanded)} className="p-1.5 rounded-lg hover:bg-[#F5F5F7] transition-colors">
            <ChevronDown className={`w-4 h-4 text-[#86868B] transition-transform ${expanded ? "rotate-180" : ""}`} />
          </button>
          <button onClick={handleCopy} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${justCopied ? "bg-green-500 text-white" : isCopied ? "bg-green-100 text-green-700 hover:bg-green-200" : "bg-[#FF6B00] text-white hover:bg-[#EA580C]"}`}>
            {justCopied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
            {justCopied ? "Copied ✓" : isCopied ? "Copy Again" : "Copy Scene"}
          </button>
        </div>
      </div>
      {expanded && (
        <div className="px-4 pb-4 border-t border-[#F5F5F7]">
          <div className="mt-3 bg-[#1D1D1F] rounded-xl p-4">
            <p className="text-[#F5F5F7] text-xs font-mono leading-relaxed whitespace-pre-wrap break-words">{promptText}</p>
          </div>
          <p className="mt-2 text-[10px] text-[#86868B]">📋 Copy → Generate in Google Flow or AI video tool → Upload back in Step 6</p>
        </div>
      )}
    </div>
  );
}

export default function StudioPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [scenes, setScenes] = useState<SceneWithStatus[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(4);
  const [copyStatus, setCopyStatus] = useState<{ total_scenes: number; copied_count: number; uploaded_count: number } | null>(null);
  const [uploadResults, setUploadResults] = useState<UploadResult[]>([]);
  const [unresolved, setUnresolved] = useState<UnresolvedFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [aiMatching, setAiMatching] = useState(false);
  const [autoAssigning, setAutoAssigning] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [assigningFile, setAssigningFile] = useState<UnresolvedFile | null>(null);
  const [assignTarget, setAssignTarget] = useState<number>(1);
  const [sequenceOrder, setSequenceOrder] = useState<number[]>([]);
  const [sequenceConfirmed, setSequenceConfirmed] = useState(false);
  const [readiness, setReadiness] = useState<AssemblyReadiness | null>(null);
  const [checkingReadiness, setCheckingReadiness] = useState(false);
  const [assembling, setAssembling] = useState(false);
  const [finalVideoResult, setFinalVideoResult] = useState<{ status: string; final_video: string; duration: number } | null>(null);
  const [assembleError, setAssembleError] = useState<string | null>(null);

  useEffect(() => {
    api.getProjects().then((list) => {
      setProjects(list);
      if (list.length > 0) setSelectedProjectId(list[0].id);
    }).catch(() => {});
  }, []);

  const loadScenes = useCallback(async () => {
    if (!selectedProjectId) return;
    setLoading(true);
    try {
      const [scenesData, statusData, readyData] = await Promise.all([
        api.getScenes(selectedProjectId),
        api.getCopyStatus(selectedProjectId),
        api.checkAssemblyReadiness(selectedProjectId).catch(() => null),
      ]);
      setScenes(scenesData as SceneWithStatus[]);
      setCopyStatus(statusData);
      setSequenceOrder(scenesData.map((s: Scene) => s.scene_number).sort((a: number, b: number) => a - b));

      if (readyData) {
        setReadiness(readyData);
        if (readyData.final_video_exists) {
          setFinalVideoResult({
            status: "completed",
            final_video: readyData.final_video_url || `/api/v1/projects/${selectedProjectId}/assembly/final-video`,
            duration: readyData.final_video_duration || 0,
          });
        } else {
          setFinalVideoResult(null);
        }

        if (readyData.unresolved_count && readyData.unresolved_count > 0) {
          api.aiMatchVideos(selectedProjectId).then((matchRes) => {
            if (matchRes.matches && matchRes.matches.length > 0) {
              setUnresolved(
                matchRes.matches.map((m) => ({
                  filename: m.filename,
                  tmp_path: m.tmp_path,
                  suggested_scene_number: m.suggested_scene_number,
                  confidence: m.confidence,
                  match_reason: m.match_reason,
                  match_source: m.match_source,
                }))
              );
            }
          }).catch(() => {});
        } else {
          setUnresolved([]);
        }
      }
    } catch { } finally { setLoading(false); }
  }, [selectedProjectId]);

  useEffect(() => { loadScenes(); }, [loadScenes]);

  const handleMarkCopied = async (sceneId: string) => {
    if (!selectedProjectId) return;
    try {
      await api.markSceneCopied(selectedProjectId, sceneId);
      setScenes((prev) => prev.map((s) => s.id === sceneId ? { ...s, prompt_status: "PROMPT_COPIED" as PromptStatus } : s));
      setCopyStatus((prev) => prev ? { ...prev, copied_count: prev.copied_count + 1 } : prev);
    } catch { }
  };

  const handleFilesDrop = async (files: FileList | null) => {
    if (!files || !selectedProjectId) return;
    setUploading(true);
    try {
      const result = await api.batchUploadScenes(selectedProjectId, Array.from(files));
      setUploadResults(result.results || []);
      setUnresolved(result.unresolved || []);
      await loadScenes();
    } catch (err: any) { alert("Upload failed: " + (err?.message || err)); }
    finally { setUploading(false); }
  };

  const handleRunAiMatch = async () => {
    if (!selectedProjectId) return;
    setAiMatching(true);
    try {
      const res = await api.aiMatchVideos(selectedProjectId);
      if (res.matches && res.matches.length > 0) {
        setUnresolved((prev) =>
          prev.map((item) => {
            const match = res.matches.find(
              (m) => m.filename === item.filename || m.tmp_path === item.tmp_path
            );
            if (match) {
              return {
                ...item,
                suggested_scene_number: match.suggested_scene_number,
                confidence: match.confidence,
                match_reason: match.match_reason,
                match_source: match.match_source,
              };
            }
            return item;
          })
        );
      }
    } catch (err: any) {
      alert("AI Matching failed: " + (err?.message || err));
    } finally {
      setAiMatching(false);
    }
  };

  const handleAutoAssignSmart = async () => {
    if (!unresolved.length || !selectedProjectId) return;
    setAutoAssigning(true);
    try {
      const assignments = unresolved.map((u) => ({
        tmp_path: u.tmp_path,
        scene_number: u.suggested_scene_number ?? 1,
        reason: u.match_reason,
      }));
      await api.autoAssignSmart(selectedProjectId, assignments);
      setUnresolved([]);
      await loadScenes();
    } catch (err: any) {
      alert("Smart assign failed: " + (err?.message || err));
    } finally {
      setAutoAssigning(false);
    }
  };

  const handleAssign = async () => {
    if (!assigningFile || !selectedProjectId) return;
    try {
      await api.assignUnresolvedVideo(selectedProjectId, assignTarget, assigningFile.tmp_path);
      setUnresolved((prev) => prev.filter((u) => u.tmp_path !== assigningFile.tmp_path));
      setAssigningFile(null);
      await loadScenes();
    } catch (err: any) { alert("Assignment failed: " + (err?.message || err)); }
  };

  const handleConfirmSequence = async () => {
    if (!selectedProjectId) return;
    try {
      await api.confirmSceneSequence(selectedProjectId, sequenceOrder);
      setSequenceConfirmed(true);
      await loadScenes();
    } catch (err: any) { alert("Failed to confirm sequence: " + (err?.message || err)); }
  };

  const handleCheckReadiness = async () => {
    if (!selectedProjectId) return;
    setCheckingReadiness(true);
    try { const r = await api.checkAssemblyReadiness(selectedProjectId); setReadiness(r); }
    catch { } finally { setCheckingReadiness(false); }
  };

  const handleGenerateFinalVideo = async () => {
    if (!selectedProjectId) return;
    setAssembling(true); setAssembleError(null);
    try { const r = await api.generateFinalVideoFromUploads(selectedProjectId); setFinalVideoResult(r); }
    catch (err: any) { setAssembleError(err?.message || "Assembly failed"); }
    finally { setAssembling(false); }
  };

  const totalScenes = scenes.length;
  const copiedCount = copyStatus?.copied_count ?? 0;
  const uploadedCount = scenes.filter((s) => s.uploaded_file).length;
  const allUploaded = totalScenes > 0 && uploadedCount >= totalScenes;
  const allCopied = totalScenes > 0 && copiedCount >= totalScenes;

  return (
    <>
      <Header title="AI Video Production Studio" subtitle="Manual Scene Generation + Automatic Assembly Workflow" />
      <main className="p-6 space-y-6 flex-1 max-w-6xl mx-auto w-full">

        {/* Project selector */}
        <div className="bg-white border border-[#E5E5EA] p-4 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xs">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#FF6B00] to-[#EA580C] flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-xs font-bold text-[#1D1D1F]">Active Project</p>
              <p className="text-[10px] text-[#86868B]">Select the project to work on</p>
            </div>
          </div>
          <select value={selectedProjectId} onChange={(e) => setSelectedProjectId(e.target.value)}
            className="border border-[#E5E5EA] rounded-xl px-3 py-2 text-sm text-[#1D1D1F] bg-white focus:outline-none focus:ring-2 focus:ring-[#FF6B00]/30 min-w-[240px]">
            {projects.map((p) => <option key={p.id} value={p.id}>{p.title || p.topic}</option>)}
          </select>
          <button onClick={loadScenes} className="flex items-center gap-2 px-4 py-2 bg-[#F5F5F7] hover:bg-[#E5E5EA] rounded-xl text-xs font-semibold text-[#1D1D1F] transition-colors">
            <RefreshCw className="w-4 h-4" /> Refresh
          </button>
        </div>

        {/* Step navigator */}
        <div className="bg-white border border-[#E5E5EA] p-4 rounded-2xl shadow-xs">
          <div className="flex gap-2 flex-wrap">
            {STEPS.map((s) => (
              <button key={s.id} onClick={() => setActiveStep(s.id)}
                className={`text-xs px-3 py-1.5 rounded-xl font-semibold transition-colors flex items-center gap-1.5 ${activeStep === s.id ? "bg-[#FF6B00] text-white shadow-md shadow-orange-500/25" : activeStep > s.id ? "bg-[#D1FAE5] text-[#065F46]" : "bg-[#F5F5F7] text-[#86868B] hover:bg-[#E5E5EA]"}`}>
                {activeStep > s.id ? <CheckCircle2 className="w-3 h-3" /> : <span>{s.id}.</span>}
                {s.label}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-16 gap-3">
            <Loader2 className="w-6 h-6 animate-spin text-[#FF6B00]" />
            <span className="text-sm text-[#86868B]">Loading project data…</span>
          </div>
        ) : (
          <>
            {/* Steps 1-3: redirect to main dashboard */}
            {activeStep <= 3 && (
              <div className="bg-[#FFF7ED] border border-[#FED7AA] rounded-2xl p-8 text-center space-y-4">
                <Sparkles className="w-10 h-10 text-[#EA580C] mx-auto" />
                <h3 className="font-bold text-[#C2410C] text-lg">Complete Steps 1–3 in the Studio Dashboard</h3>
                <p className="text-sm text-[#86868B] max-w-md mx-auto">Topic selection, SEO metadata, song generation, and SRT/lyrics are managed in the main Studio Dashboard (10-Step workflow).</p>
                <a href="/" className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#FF6B00] text-white rounded-xl font-semibold text-sm hover:bg-[#EA580C] transition-colors">
                  <ArrowRight className="w-4 h-4" /> Go to Studio Dashboard
                </a>
              </div>
            )}

            {/* Steps 4 & 5: Scene Prompts + Copy Tracking */}
            {(activeStep === 4 || activeStep === 5) && (
              <div className="space-y-4">
                <div className="bg-white border border-[#E5E5EA] rounded-2xl p-4 flex items-center justify-between flex-wrap gap-4">
                  <div className="flex items-center gap-6">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-[#1D1D1F]">{totalScenes}</p>
                      <p className="text-[10px] text-[#86868B] font-semibold uppercase tracking-wide">Total Scenes</p>
                    </div>
                    <div className="w-px h-8 bg-[#E5E5EA]" />
                    <div className="text-center">
                      <p className={`text-2xl font-bold ${allCopied ? "text-green-600" : "text-[#1D1D1F]"}`}>{copiedCount} / {totalScenes}</p>
                      <p className="text-[10px] text-[#86868B] font-semibold uppercase tracking-wide">Prompts Copied</p>
                    </div>
                    <div className="w-px h-8 bg-[#E5E5EA]" />
                    <div className="text-center">
                      <p className={`text-2xl font-bold ${allUploaded ? "text-purple-600" : "text-[#1D1D1F]"}`}>{uploadedCount} / {totalScenes}</p>
                      <p className="text-[10px] text-[#86868B] font-semibold uppercase tracking-wide">Videos Uploaded</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {allCopied && <span className="flex items-center gap-1.5 text-xs font-semibold text-green-700 bg-green-100 px-3 py-1.5 rounded-full"><CheckCircle2 className="w-3.5 h-3.5" />All prompts copied ✓</span>}
                    <button onClick={() => { const all = scenes.map((s) => `=== SCENE ${String(s.scene_number).padStart(2, "0")} ===\n${s.video_prompt || s.dialogue || s.lyrics || ""}`).join("\n\n"); navigator.clipboard.writeText(all); }}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-[#F5F5F7] hover:bg-[#E5E5EA] rounded-xl text-xs font-semibold text-[#1D1D1F] transition-colors">
                      <Copy className="w-3.5 h-3.5" /> Copy All Prompts
                    </button>
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4 flex items-start gap-3">
                  <ExternalLink className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-blue-800"><strong>Workflow:</strong> Copy each scene prompt → Generate video in <a href="https://labs.google/flow/" target="_blank" rel="noopener noreferrer" className="underline font-semibold">Google Flow</a> or any AI video tool → Upload back in Step 6. Zero API key required.</p>
                </div>

                {scenes.length === 0 ? (
                  <div className="bg-[#FFF7ED] border border-[#FED7AA] rounded-2xl p-8 text-center">
                    <Clapperboard className="w-8 h-8 text-[#EA580C] mx-auto mb-3" />
                    <p className="font-semibold text-[#C2410C] mb-1">No scenes yet</p>
                    <p className="text-sm text-[#86868B]">Generate your storyboard first from the Studio Dashboard.</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {scenes.map((scene) => (
                      <ScenePromptCard key={scene.id} scene={scene} onCopied={handleMarkCopied} />
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Step 6: Upload */}
            {activeStep === 6 && (
              <div className="space-y-4">
                <div className="bg-white border border-[#E5E5EA] rounded-2xl p-4">
                  <h2 className="font-bold text-[#1D1D1F] mb-1 flex items-center gap-2"><UploadCloud className="w-5 h-5 text-[#FF6B00]" />Upload Generated Scene Videos</h2>
                  <p className="text-sm text-[#86868B]">Files named <code className="bg-[#F5F5F7] px-1 rounded text-xs">scene_01.mp4</code>, <code className="bg-[#F5F5F7] px-1 rounded text-xs">scene-02.mp4</code> etc. are mapped automatically. Random names prompt manual assignment.</p>
                </div>

                <div onDragOver={(e) => { e.preventDefault(); setDragOver(true); }} onDragLeave={() => setDragOver(false)}
                  onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFilesDrop(e.dataTransfer.files); }}
                  onClick={() => fileInputRef.current?.click()}
                  className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${dragOver ? "border-[#FF6B00] bg-[#FFF7ED]" : "border-[#C7C7CC] bg-[#FAFAFC] hover:border-[#FF6B00] hover:bg-[#FFF7ED]"}`}>
                  <input ref={fileInputRef} type="file" accept="video/mp4,video/quicktime,video/webm,.mp4,.mov,.webm" multiple className="hidden" onChange={(e) => handleFilesDrop(e.target.files)} />
                  {uploading ? (
                    <div className="flex flex-col items-center gap-3"><Loader2 className="w-10 h-10 text-[#FF6B00] animate-spin" /><p className="font-semibold text-[#1D1D1F]">Uploading and processing…</p></div>
                  ) : (
                    <div className="flex flex-col items-center gap-3">
                      <UploadCloud className="w-10 h-10 text-[#C7C7CC]" />
                      <div><p className="font-bold text-[#1D1D1F]">Drag &amp; Drop</p><p className="text-sm text-[#86868B]">or click to Browse Files</p></div>
                      <p className="text-xs text-[#86868B]">MP4, MOV, WEBM — multiple files allowed</p>
                    </div>
                  )}
                </div>

                {uploadResults.length > 0 && (
                  <div className="bg-white border border-[#E5E5EA] rounded-2xl overflow-hidden">
                    <div className="p-4 border-b border-[#F5F5F7]"><h3 className="font-bold text-[#1D1D1F] text-sm">Upload Results</h3></div>
                    <div className="divide-y divide-[#F5F5F7]">
                      {uploadResults.map((r, i) => (
                        <div key={i} className="flex items-center justify-between px-4 py-3">
                          <div className="flex items-center gap-3"><FileVideo className="w-4 h-4 text-[#86868B]" /><span className="text-sm text-[#1D1D1F] font-medium">{r.filename}</span></div>
                          <div className="flex items-center gap-2">
                            {r.scene_number && <span className="text-xs text-[#86868B]">→ Scene {r.scene_number}</span>}
                            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${r.status === "UPLOADED" ? "bg-green-100 text-green-700" : r.status === "NEEDS_ASSIGNMENT" ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"}`}>
                              {r.status === "UPLOADED" ? "✓ Uploaded" : r.status === "NEEDS_ASSIGNMENT" ? "⚠ Needs Assignment" : "✗ Rejected"}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {unresolved.length > 0 && (
                  <div className="bg-gradient-to-br from-indigo-50/70 via-orange-50/50 to-amber-50/80 border border-orange-200/80 rounded-2xl p-4 space-y-3">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-orange-200/50">
                      <div>
                        <h3 className="font-bold text-[#1D1D1F] text-sm flex items-center gap-2">
                          <Sparkles className="w-4 h-4 text-[#FF6B00]" />
                          AI Scene Matcher ({unresolved.length} clips)
                        </h3>
                        <p className="text-xs text-[#6E6E73]">
                          AI matched video titles with scene prompts and lyrics.
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={handleRunAiMatch}
                          disabled={aiMatching}
                          className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-colors flex items-center gap-1.5 disabled:opacity-50"
                        >
                          {aiMatching ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                          <span>{aiMatching ? "Matching…" : "Re-Match AI"}</span>
                        </button>
                        <button
                          onClick={handleAutoAssignSmart}
                          disabled={autoAssigning}
                          className="px-3.5 py-1.5 bg-gradient-to-r from-orange-500 to-amber-600 hover:opacity-90 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shadow-xs disabled:opacity-50"
                        >
                          {autoAssigning ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
                          <span>{autoAssigning ? "Assigning…" : "⚡ Apply AI Matches"}</span>
                        </button>
                      </div>
                    </div>

                    <div className="space-y-2">
                      {unresolved.map((u) => {
                        const targetSceneNum = u.suggested_scene_number ?? 1;
                        const matchedScene = scenes.find((s) => s.scene_number === targetSceneNum);
                        const confidence = u.confidence ?? 50;

                        return (
                          <div key={u.tmp_path} className="bg-white/90 rounded-xl p-3 border border-orange-200/70 space-y-1.5 shadow-2xs">
                            <div className="flex items-center justify-between gap-2">
                              <div className="flex items-center gap-2 min-w-0">
                                <FileVideo className="w-4 h-4 text-indigo-600 shrink-0" />
                                <span className="text-sm font-semibold text-[#1D1D1F] truncate" title={u.filename}>
                                  {u.filename}
                                </span>
                                {u.duration && <span className="text-xs text-[#86868B]">({u.duration.toFixed(1)}s)</span>}
                                {u.confidence && (
                                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${confidence >= 80 ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800"}`}>
                                    {Math.round(confidence)}% Match → Scene {targetSceneNum}
                                  </span>
                                )}
                              </div>
                              <button
                                onClick={() => { setAssigningFile(u); setAssignTarget(targetSceneNum); }}
                                className="px-3 py-1 bg-[#FF6B00] text-white rounded-xl text-xs font-semibold hover:bg-[#EA580C] transition-colors shrink-0"
                              >
                                Assign to Scene {targetSceneNum}
                              </button>
                            </div>

                            {u.match_reason && (
                              <p className="text-[11px] text-indigo-900 bg-indigo-50/70 px-2 py-1 rounded-md">
                                <span className="font-bold">AI Reason:</span> {u.match_reason}
                              </p>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {scenes.length > 0 && (
                  <div className="bg-white border border-[#E5E5EA] rounded-2xl p-4">
                    <h3 className="font-bold text-[#1D1D1F] mb-3 flex items-center gap-2 text-sm"><Layers className="w-4 h-4 text-[#FF6B00]" />Scene Upload Status</h3>
                    <div className="space-y-2">
                      {scenes.map((s) => (
                        <div key={s.id} className="flex items-center justify-between px-4 py-3 rounded-xl border border-[#F5F5F7] bg-[#FAFAFC]">
                          <div className="flex items-center gap-3">
                            <span className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${s.uploaded_file ? "bg-green-100 text-green-700" : "bg-[#F5F5F7] text-[#86868B]"}`}>{String(s.scene_number).padStart(2, "0")}</span>
                            <div>
                              <p className="text-xs font-semibold text-[#1D1D1F]">{s.lyrics ? `"${s.lyrics}"` : `Scene ${s.scene_number}`}</p>
                              <p className="text-[10px] text-[#86868B]">Planned: {s.duration?.toFixed(1)}s{s.uploaded_duration ? ` · Uploaded: ${s.uploaded_duration.toFixed(1)}s` : ""}</p>
                            </div>
                          </div>
                          {s.uploaded_file ? <span className="text-xs bg-green-100 text-green-700 px-2.5 py-1 rounded-full font-semibold">✓ Uploaded</span> : <span className="text-xs bg-[#F5F5F7] text-[#86868B] px-2.5 py-1 rounded-full font-medium">○ Missing</span>}
                        </div>
                      ))}
                    </div>
                    {!allUploaded && <p className="mt-3 text-sm text-red-600 font-medium flex items-center gap-1.5"><AlertTriangle className="w-4 h-4" />{totalScenes - uploadedCount} scene(s) still missing.</p>}
                  </div>
                )}
              </div>
            )}

            {/* Step 7: Verify Order */}
            {activeStep === 7 && (
              <div className="space-y-4">
                <div className="bg-white border border-[#E5E5EA] rounded-2xl p-4">
                  <h2 className="font-bold text-[#1D1D1F] mb-1 flex items-center gap-2"><ListOrdered className="w-5 h-5 text-[#FF6B00]" />Verify Scene Sequence</h2>
                  <p className="text-sm text-[#86868B]">Scenes are auto-ordered by number. Confirm the sequence before generating the final video.</p>
                </div>
                <div className="bg-white border border-[#E5E5EA] rounded-2xl p-4 space-y-4">
                  <div className="flex items-center gap-2 flex-wrap">
                    {sequenceOrder.map((num, idx) => (
                      <div key={num} className="flex items-center gap-1">
                        <div className={`px-3 py-1.5 rounded-xl text-xs font-bold border ${scenes.find(s => s.scene_number === num)?.uploaded_file ? "bg-green-100 text-green-800 border-green-200" : "bg-red-50 text-red-600 border-red-200"}`}>
                          {String(num).padStart(2, "0")}{!scenes.find(s => s.scene_number === num)?.uploaded_file && " ⚠"}
                        </div>
                        {idx < sequenceOrder.length - 1 && <ArrowRight className="w-3 h-3 text-[#C7C7CC]" />}
                      </div>
                    ))}
                  </div>
                  {!allUploaded && (
                    <div className="bg-red-50 border border-red-200 rounded-xl p-3">
                      <p className="text-sm text-red-700 font-semibold flex items-center gap-2"><AlertTriangle className="w-4 h-4" />{totalScenes - uploadedCount} scene(s) missing:</p>
                      <p className="text-xs text-red-600 mt-1">{scenes.filter(s => !s.uploaded_file).map(s => `Scene ${s.scene_number}`).join(", ")}</p>
                    </div>
                  )}
                  <button disabled={!allUploaded || sequenceConfirmed} onClick={handleConfirmSequence}
                    className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-sm transition-all ${allUploaded && !sequenceConfirmed ? "bg-[#FF6B00] text-white hover:bg-[#EA580C] shadow-md shadow-orange-500/25" : sequenceConfirmed ? "bg-green-500 text-white cursor-default" : "bg-[#F5F5F7] text-[#86868B] cursor-not-allowed"}`}>
                    {sequenceConfirmed ? <><CheckCircle2 className="w-4 h-4" />Sequence Confirmed ✓</> : <><Check className="w-4 h-4" />Confirm Sequence</>}
                  </button>
                </div>
              </div>
            )}

            {/* Step 8: Final Video */}
            {activeStep === 8 && (
              <div className="space-y-4">
                <div className="bg-white border border-[#E5E5EA] rounded-2xl p-4">
                  <h2 className="font-bold text-[#1D1D1F] mb-1 flex items-center gap-2"><Film className="w-5 h-5 text-[#FF6B00]" />Generate Final Video</h2>
                  <p className="text-sm text-[#86868B]">Combines uploaded scene videos + song audio + SRT subtitles using FFmpeg. No AI API required.</p>
                </div>

                <div className="bg-white border border-[#E5E5EA] rounded-2xl p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-sm text-[#1D1D1F]">Pre-flight Checklist</h3>
                    <button onClick={handleCheckReadiness} disabled={checkingReadiness} className="flex items-center gap-1.5 px-3 py-1.5 bg-[#F5F5F7] hover:bg-[#E5E5EA] rounded-xl text-xs font-semibold text-[#1D1D1F] transition-colors">
                      {checkingReadiness ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />} Check Readiness
                    </button>
                  </div>
                  {readiness ? (
                    <div className="space-y-2">
                      {[
                        { label: `Scene videos: ${readiness.uploaded_scenes}/${readiness.total_scenes} uploaded`, ok: readiness.uploaded_scenes === readiness.total_scenes && readiness.total_scenes > 0 },
                        { label: "Audio / song available", ok: readiness.audio_available },
                        { label: "SRT / subtitles available", ok: readiness.srt_available },
                        { label: "Sequence confirmed", ok: readiness.sequence_confirmed || sequenceConfirmed },
                      ].map((item, i) => (
                        <div key={i} className="flex items-center gap-3">
                          {item.ok ? <CheckCircle2 className="w-4 h-4 text-green-500" /> : <Circle className="w-4 h-4 text-[#C7C7CC]" />}
                          <span className={`text-sm ${item.ok ? "text-[#1D1D1F]" : "text-[#86868B]"}`}>{item.label}</span>
                        </div>
                      ))}
                      {readiness.missing_scenes.length > 0 && (
                        <div className="bg-red-50 border border-red-200 rounded-xl p-3 mt-2">
                          <p className="text-sm text-red-700 font-semibold">Missing: {readiness.missing_scenes.map(n => `Scene ${n}`).join(", ")}</p>
                        </div>
                      )}
                    </div>
                  ) : <p className="text-sm text-[#86868B]">Click "Check Readiness" to validate before assembling.</p>}
                </div>

                {!finalVideoResult && (
                  <button onClick={handleGenerateFinalVideo} disabled={assembling || (readiness != null && !readiness.ready)}
                    className={`w-full flex items-center justify-center gap-3 py-4 rounded-2xl font-bold text-base transition-all ${assembling ? "bg-[#FF6B00]/70 text-white cursor-not-allowed" : readiness && !readiness.ready ? "bg-[#F5F5F7] text-[#86868B] cursor-not-allowed" : "bg-gradient-to-r from-[#FF6B00] to-[#EA580C] text-white shadow-lg shadow-orange-500/30 hover:shadow-orange-500/40 hover:-translate-y-0.5"}`}>
                    {assembling ? <><Loader2 className="w-5 h-5 animate-spin" />Assembling Final Video… (may take a few minutes)</> : <><Zap className="w-5 h-5" />Generate Final Video</>}
                  </button>
                )}

                {assembleError && (
                  <div className="bg-red-50 border border-red-200 rounded-2xl p-4">
                    <p className="font-bold text-red-700 mb-1 flex items-center gap-2"><AlertTriangle className="w-4 h-4" />Assembly Failed</p>
                    <p className="text-sm text-red-600">{assembleError}</p>
                    <button onClick={handleGenerateFinalVideo} className="mt-3 px-4 py-2 bg-red-600 text-white rounded-xl text-sm font-semibold hover:bg-red-700 transition-colors">Retry Final Video</button>
                  </div>
                )}

                {finalVideoResult && (
                  <div className="bg-green-50 border border-green-200 rounded-2xl p-6 text-center space-y-4">
                    <CheckCircle2 className="w-12 h-12 text-green-500 mx-auto" />
                    <h3 className="text-lg font-bold text-green-800">Final Video Ready ✓</h3>
                    {finalVideoResult.duration && <p className="text-3xl font-bold text-green-700">{finalVideoResult.duration.toFixed(1)}s</p>}
                    <a href={api.getFinalVideoUrl(selectedProjectId)} target="_blank" rel="noopener noreferrer" download
                      className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-xl font-semibold hover:bg-green-700 transition-colors">
                      <Play className="w-4 h-4" /> Download / Open Final Video
                    </a>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </main>

      {/* Assignment Modal */}
      {assigningFile && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-[#1D1D1F]">Which scene does this belong to?</h3>
              <button onClick={() => setAssigningFile(null)} className="p-1.5 hover:bg-[#F5F5F7] rounded-lg"><X className="w-4 h-4 text-[#86868B]" /></button>
            </div>
            <p className="text-sm text-[#86868B]"><strong className="text-[#1D1D1F]">{assigningFile.filename}</strong>{assigningFile.duration ? ` (${assigningFile.duration.toFixed(1)}s)` : ""}</p>
            <div className="grid grid-cols-4 gap-2">
              {scenes.map((s) => (
                <button key={s.scene_number} onClick={() => setAssignTarget(s.scene_number)}
                  className={`py-2 rounded-xl text-sm font-bold transition-colors ${assignTarget === s.scene_number ? "bg-[#FF6B00] text-white" : "bg-[#F5F5F7] text-[#1D1D1F] hover:bg-[#E5E5EA]"}`}>
                  {String(s.scene_number).padStart(2, "0")}
                </button>
              ))}
            </div>
            <div className="flex gap-3">
              <button onClick={() => setAssigningFile(null)} className="flex-1 py-2.5 rounded-xl border border-[#E5E5EA] text-sm font-semibold text-[#6E6E73] hover:bg-[#F5F5F7] transition-colors">Cancel</button>
              <button onClick={handleAssign} className="flex-1 py-2.5 rounded-xl bg-[#FF6B00] text-white text-sm font-semibold hover:bg-[#EA580C] transition-colors">Assign to Scene {String(assignTarget).padStart(2, "0")}</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
