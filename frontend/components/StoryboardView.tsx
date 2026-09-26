"use client";

import { useState, useEffect } from "react";
import { Scene, AISettings } from "@/lib/types";
import { api, API_BASE } from "@/lib/api";
import {
  Clapperboard,
  RotateCcw,
  CheckCircle2,
  Clock,
  Camera,
  Users2,
  Tv,
  AlertCircle,
  Loader2,
  Sparkles,
  Copy,
  Check,
  Film,
  Video,
  Cpu,
  Zap,
  UploadCloud,
  Download,
  AlertTriangle,
  ListOrdered,
  X,
  ExternalLink,
  ImageIcon,
  Upload,
} from "lucide-react";

interface StoryboardViewProps {
  projectId: string;
  scenes: Scene[];
  onSceneRerendered?: () => void;
  onScenesUpdated?: (scenes: Scene[]) => void;
  initialSceneDuration?: number;
}

export function StoryboardView({
  projectId,
  scenes,
  onSceneRerendered,
  onScenesUpdated,
  initialSceneDuration = 8,
}: StoryboardViewProps) {
  const [sceneDuration, setSceneDuration] = useState<number>(initialSceneDuration);
  const [regeneratingStoryboard, setRegeneratingStoryboard] = useState(false);
  const [rerenderingId, setRerenderingId] = useState<string | null>(null);
  const [validationResult, setValidationResult] = useState<{ is_valid: boolean; errors: string[] } | null>(null);
  const [validating, setValidating] = useState(false);
  const [copiedAll, setCopiedAll] = useState(false);
  const [copiedAllPrompts, setCopiedAllPrompts] = useState(false);
  const [copiedSceneId, setCopiedSceneId] = useState<string | null>(null);
  const [copiedPromptId, setCopiedPromptId] = useState<string | null>(null);
  const [aiSettings, setAiSettings] = useState<AISettings | null>(null);

  // Manual workflow state inside Storyboard
  const [copyStatus, setCopyStatus] = useState<{ total_scenes: number; copied_count: number; uploaded_count: number } | null>(null);
  const [uploadingVideos, setUploadingVideos] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [unresolved, setUnresolved] = useState<
    Array<{
      filename: string;
      tmp_path: string;
      duration?: number;
      suggested_scene_number?: number;
      confidence?: number;
      match_reason?: string;
      match_source?: string;
    }>
  >([]);
  const [fileSceneMap, setFileSceneMap] = useState<Record<string, number>>({});
  const [autoAssigning, setAutoAssigning] = useState(false);
  const [aiMatching, setAiMatching] = useState(false);
  const [sequenceConfirmed, setSequenceConfirmed] = useState(false);
  const [confirmingSequence, setConfirmingSequence] = useState(false);
  const [assembling, setAssembling] = useState(false);
  const [finalVideoResult, setFinalVideoResult] = useState<{ status: string; final_video: string; duration: number } | null>(null);
  const [assembleError, setAssembleError] = useState<string | null>(null);

  const handleRunAiMatch = async () => {
    if (!projectId) return;
    setAiMatching(true);
    try {
      const res = await api.aiMatchVideos(projectId);
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
        const newMap: Record<string, number> = {};
        res.matches.forEach((m) => {
          if (m.tmp_path) newMap[m.tmp_path] = m.suggested_scene_number;
        });
        setFileSceneMap((prev) => ({ ...prev, ...newMap }));
      }
    } catch (err: any) {
      alert("AI Matching failed: " + (err?.message || err));
    } finally {
      setAiMatching(false);
    }
  };

  const handleAutoAssignAll = async () => {
    if (!unresolved.length || !projectId) return;
    setAutoAssigning(true);
    try {
      const assignments = unresolved.map((u) => ({
        tmp_path: u.tmp_path,
        scene_number: fileSceneMap[u.tmp_path] ?? u.suggested_scene_number ?? 1,
        reason: u.match_reason,
      }));
      await api.autoAssignSmart(projectId, assignments);
      setUnresolved([]);
      const updated = await api.getScenes(projectId);
      if (onScenesUpdated) onScenesUpdated(updated);
      const st = await api.getCopyStatus(projectId);
      setCopyStatus(st);
    } catch (err: any) {
      alert("Smart AI assign failed: " + (err?.message || err));
    } finally {
      setAutoAssigning(false);
    }
  };

  useEffect(() => {
    api.getAISettings().then(setAiSettings).catch(() => {});
    if (projectId) {
      api.getCopyStatus(projectId).then(setCopyStatus).catch(() => {});
      api.checkAssemblyReadiness(projectId).then((readyData) => {
        if (readyData.final_video_exists) {
          setFinalVideoResult({
            status: "completed",
            final_video: readyData.final_video_url || `${API_BASE}/api/v1/projects/${projectId}/assembly/final-video`,
            duration: readyData.final_video_duration || 0,
          });
        } else {
          setFinalVideoResult(null);
        }

        if (readyData.unresolved_count && readyData.unresolved_count > 0) {
          api.aiMatchVideos(projectId).then((matchRes) => {
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
              const newMap: Record<string, number> = {};
              matchRes.matches.forEach((m) => {
                if (m.tmp_path) newMap[m.tmp_path] = m.suggested_scene_number;
              });
              setFileSceneMap((prev) => ({ ...prev, ...newMap }));
            }
          }).catch(() => {});
        } else {
          setUnresolved([]);
        }
      }).catch(() => {});
    }
  }, [projectId]);

  const handleRegenerateStoryboard = async (dur: number) => {
    setSceneDuration(dur);
    setRegeneratingStoryboard(true);
    try {
      const updated = await api.generateStoryboard(projectId, dur);
      if (onScenesUpdated) {
        onScenesUpdated(updated);
      }
    } catch (err: any) {
      alert("Failed to regenerate storyboard: " + (err?.message || err));
    } finally {
      setRegeneratingStoryboard(false);
    }
  };

  const handleRerender = async (sceneId: string, sceneNum: number) => {
    setRerenderingId(sceneId);
    try {
      await api.rerenderScene(sceneId);
      if (onSceneRerendered) onSceneRerendered();
    } catch (err: any) {
      alert(`Scene ${sceneNum} re-render failed: ` + err.message);
    } finally {
      setRerenderingId(null);
    }
  };

  const handleValidate = async () => {
    setValidating(true);
    try {
      const res = await api.validateStoryboard(projectId);
      setValidationResult(res);
    } catch (err: any) {
      console.error("Validation failed:", err);
    } finally {
      setValidating(false);
    }
  };

  const getVideoPrompt = (sc: Scene): string => {
    if (sc.video_prompt && sc.video_prompt.trim().length > 30) {
      return sc.video_prompt.trim();
    }
    const characters = Array.isArray(sc.characters)
      ? sc.characters.map((c: any) => (typeof c === "object" ? c.name || c.character_id : c)).join(", ")
      : sc.characters || "Cute toddler preschool character";
    const camera = typeof sc.camera === "object" && sc.camera ? `${sc.camera.shot || "medium"} ${sc.camera.movement || "push-in"}` : "smooth cinematic tracking";
    const actions = Array.isArray(sc.actions) ? sc.actions.join("; ") : "dancing cheerfully and waving at the camera";
    const lyrics = sc.lyrics || sc.dialogue || "Joyful nursery rhyme melody";
    const env = sc.environment || "Vibrant preschool storybook meadow";

    return `3D Pixar Disney style CGI animation: ${characters}, cute expressive face, big sparkling eyes, colorful preschool outfit. Visual View & Action: Character is ${actions} in lively synchronization with '${lyrics}'. Environment: ${env} filled with playful animated props, toy flowers, and pastel clouds. Cinematography: ${camera}, warm soft golden sunlight, gentle rim light, raytraced subsurface scattering, vibrant saturated colors, 8k ultra-detailed nursery rhyme render.`;
  };

  const handleCopyVideoPrompt = async (sc: Scene) => {
    const prompt = getVideoPrompt(sc);
    navigator.clipboard.writeText(prompt);
    setCopiedPromptId(sc.id);
    setTimeout(() => setCopiedPromptId(null), 2000);
    try {
      await api.markSceneCopied(projectId, sc.id);
      if (onScenesUpdated) {
        onScenesUpdated(scenes.map(s => s.id === sc.id ? { ...s, prompt_status: 'PROMPT_COPIED' } : s));
      }
      const st = await api.getCopyStatus(projectId);
      setCopyStatus(st);
    } catch (e) {
      console.error("Mark scene copied failed:", e);
    }
  };

  const handleCopyAllVideoPrompts = () => {
    if (!scenes || scenes.length === 0) return;
    const text = scenes
      .map((sc) => {
        const p = getVideoPrompt(sc);
        return `### SCENE ${sc.scene_number.toString().padStart(2, "0")} (${sc.duration.toFixed(1)}s)
Lyrics: "${sc.lyrics || sc.dialogue || ""}"
AI Video Generation Prompt:
${p}`;
      })
      .join("\n\n");
    navigator.clipboard.writeText(text);
    setCopiedAllPrompts(true);
    setTimeout(() => setCopiedAllPrompts(false), 2000);
  };

  const handleCopyAllScenes = () => {
    if (!scenes || scenes.length === 0) return;
    const formatted = scenes
      .map((sc) => {
        const characters = Array.isArray(sc.characters)
          ? sc.characters.map((c: any) => (typeof c === "object" ? c.name || c.character_id : c)).join(", ")
          : sc.characters || "None";
        const camera = typeof sc.camera === "object" && sc.camera ? `${sc.camera.shot || "wide"} • ${sc.camera.movement || "orbit"}` : "Standard";
        const actions = Array.isArray(sc.actions) ? sc.actions.join("; ") : "Dancing & singing";
        const prompt = getVideoPrompt(sc);

        return `--- SCENE ${sc.scene_number.toString().padStart(2, "0")} (${sc.duration.toFixed(1)}s) ---
Lyrics / Dialogue: "${sc.lyrics || sc.dialogue || "Instrumental animation cue"}"
Environment: ${sc.environment || "Preschool Meadow"}
Characters: ${characters}
Camera: ${camera}
Action / Choreography: ${actions}
AI Video Generation Prompt:
${prompt}
Status: ${sc.status}`;
      })
      .join("\n\n");

    navigator.clipboard.writeText(formatted);
    setCopiedAll(true);
    setTimeout(() => setCopiedAll(false), 2000);
  };

  const handleCopySingleScene = (sc: Scene) => {
    const characters = Array.isArray(sc.characters)
      ? sc.characters.map((c: any) => (typeof c === "object" ? c.name || c.character_id : c)).join(", ")
      : sc.characters || "None";
    const camera = typeof sc.camera === "object" && sc.camera ? `${sc.camera.shot || "wide"} • ${sc.camera.movement || "orbit"}` : "Standard";
    const actions = Array.isArray(sc.actions) ? sc.actions.join("; ") : "Dancing & singing";
    const prompt = getVideoPrompt(sc);

    const text = `Scene ${sc.scene_number} (${sc.duration.toFixed(1)}s)
Lyrics: "${sc.lyrics || sc.dialogue || "Instrumental cue"}"
Characters: ${characters}
Environment: ${sc.environment}
Camera: ${camera}
Actions: ${actions}
Video Prompt:
${prompt}`;

    navigator.clipboard.writeText(text);
    setCopiedSceneId(sc.id);
    setTimeout(() => setCopiedSceneId(null), 2000);
  };

  return (
    <div className="bg-white border border-[#E5E5EA] rounded-3xl p-6 shadow-xs space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-[#E5E5EA]">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-purple-50 text-purple-800 border border-purple-200">
            <Clapperboard className="w-3.5 h-3.5 text-purple-600" />
            <span>Step 4 • Storyboard & 3D Video Generation Prompts</span>
          </div>
          <h2 className="text-lg font-bold text-[#1D1D1F]">
            3D Scene Storyboard Shots ({scenes.length} Shots)
          </h2>
          <p className="text-xs text-[#6E6E73]">
            Each scene contains a dedicated 3D Stylized Preschool Video Generation Prompt describing character actions, environment view, and camera angles for video AI tools (Luma, Kling, Seedance, Runway, Sora).
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Copy All Video Prompts */}
          <button
            onClick={handleCopyAllVideoPrompts}
            className="inline-flex items-center gap-1.5 bg-orange-50 hover:bg-orange-100 text-orange-800 border border-orange-200 text-xs font-bold px-3.5 py-2 rounded-xl transition-all cursor-pointer shadow-2xs"
            title="Copy all scenes video generation prompts to clipboard for batch video generation"
          >
            {copiedAllPrompts ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Film className="w-3.5 h-3.5 text-orange-600" />}
            <span>{copiedAllPrompts ? "All Prompts Copied!" : "Copy All Video Prompts"}</span>
          </button>

          {/* Copy Full Storyboard */}
          <button
            onClick={handleCopyAllScenes}
            className="inline-flex items-center gap-1.5 bg-purple-50 hover:bg-purple-100 text-purple-800 border border-purple-200 text-xs font-bold px-3.5 py-2 rounded-xl transition-all cursor-pointer"
          >
            {copiedAll ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-purple-600" />}
            <span>{copiedAll ? "Storyboard Copied!" : "Copy Storyboard"}</span>
          </button>

          <button
            onClick={handleValidate}
            disabled={validating}
            className="inline-flex items-center gap-1.5 bg-[#FAFAFC] hover:bg-[#F5F5F7] text-[#1D1D1F] border border-[#E5E5EA] text-xs font-semibold px-3.5 py-2 rounded-xl transition-colors cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5 text-[#FF6B00]" />
            <span>{validating ? "Validating..." : "Validate Mapping"}</span>
          </button>
        </div>
      </div>

      {/* PER-SCENE DURATION FILTER BAR */}
      <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-2xs">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-blue-600 shrink-0" />
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-xs font-bold text-[#1E293B]">
                Per-Scene Target Duration Filter:
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">
                Current: {sceneDuration}s / scene
              </span>
            </div>
            <p className="text-[11px] text-[#64748B]">
              Controls pacing, lyric chunking, and clip length before video generation (8s, 9s, 10s).
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-1.5">
          {[6, 7, 8, 9, 10, 12].map((dur) => (
            <button
              key={dur}
              onClick={() => handleRegenerateStoryboard(dur)}
              disabled={regeneratingStoryboard}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                sceneDuration === dur
                  ? "bg-blue-600 text-white shadow-xs"
                  : "bg-white text-[#475569] border border-[#CBD5E1] hover:bg-blue-50 hover:text-blue-700"
              } disabled:opacity-50`}
            >
              {dur}s {dur === 8 ? "★" : ""}
            </button>
          ))}

          <button
            onClick={() => handleRegenerateStoryboard(sceneDuration)}
            disabled={regeneratingStoryboard}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:opacity-95 text-white rounded-xl text-xs font-bold shadow-xs transition-all cursor-pointer disabled:opacity-50 ml-1"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${regeneratingStoryboard ? "animate-spin" : ""}`} />
            <span>{regeneratingStoryboard ? "Re-Planning..." : `Apply (${sceneDuration}s)`}</span>
          </button>
        </div>
      </div>

      {/* ACTIVE AI ENGINE INFORMATION BAR */}
      <div className="bg-[#FAF5FF] border border-[#E9D5FF] rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-2xs">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center shrink-0">
            <Video className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-bold text-[#1D1D1F]">
                Active AI Video Engine:
              </span>
              <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-purple-200/70 text-purple-900 font-mono">
                {aiSettings?.use_wan_video || aiSettings?.video_provider === "wan"
                  ? `Wan 2.1 FLF2V (${aiSettings?.wan_model || "fal-ai/wan-flf2v"})`
                  : "Local Storybook 3D Engine (Instant)"}
              </span>
              {aiSettings?.ai_provider_test_mode && (
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">
                  ⚡ Fast Test Mode
                </span>
              )}
            </div>
            <p className="text-[11px] text-[#6E6E73] mt-0.5">
              {aiSettings?.use_wan_video || aiSettings?.video_provider === "wan"
                ? "Cloud AI Diffusion Engine: Generates full photorealistic 3D video (~20-40s per scene). You can switch to Instant Local 3D in Settings."
                : "Local Storybook Engine: Generates instant 3D video previews on Apple Silicon."}
            </p>
          </div>
        </div>

        <a
          href="/settings"
          className="inline-flex items-center gap-1 text-xs font-semibold text-purple-700 hover:text-purple-900 bg-white border border-[#E9D5FF] px-3 py-1.5 rounded-xl transition-all shrink-0 self-start sm:self-auto"
        >
          <Cpu className="w-3.5 h-3.5" />
          <span>Change AI Model</span>
        </a>
      </div>

      {validationResult && (
        <div
          className={`p-4 rounded-2xl border text-xs font-semibold ${
            validationResult.is_valid
              ? "bg-emerald-50 border-emerald-200 text-emerald-800"
              : "bg-amber-50 border-amber-200 text-amber-800"
          }`}
        >
          <div className="flex items-center gap-2">
            {validationResult.is_valid ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
            )}
            <span>
              {validationResult.is_valid
                ? "Storyboard Validation Passed: Perfect timeline continuity and Character Bible adherence."
                : `Validation Notice (${validationResult.errors.length} items):`}
            </span>
          </div>
          {!validationResult.is_valid && (
            <ul className="mt-2 list-disc list-inside space-y-1 text-[11px] font-normal">
              {validationResult.errors.map((e, idx) => (
                <li key={idx}>{e}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Scenes Timeline Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4.5">
        {scenes.map((sc, idx) => {
          const isCompleted = sc.status === "COMPLETED";
          const isRendering = rerenderingId === sc.id;
          const isCopied = copiedSceneId === sc.id;
          const isPromptCopied = copiedPromptId === sc.id;
          const videoPrompt = getVideoPrompt(sc);

          return (
            <div
              key={sc.id || idx}
              className={`bg-[#FAFAFC] border rounded-2xl p-4.5 flex flex-col justify-between space-y-3.5 transition-all shadow-2xs hover:shadow-xs ${
                isCompleted ? "border-emerald-200 bg-emerald-50/10" : "border-[#E5E5EA]"
              }`}
            >
              <div className="space-y-3">
                {/* Scene Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-extrabold text-xs text-[#1D1D1F]">
                      Scene {sc.scene_number.toString().padStart(2, "0")}
                    </span>
                    <button
                      type="button"
                      onClick={() => handleCopySingleScene(sc)}
                      className="text-[#86868B] hover:text-[#1D1D1F] p-0.5 rounded cursor-pointer"
                      title="Copy entire scene data"
                    >
                      {isCopied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-bold text-[#86868B] flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {sc.duration.toFixed(1)}s
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        isCompleted
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-amber-100 text-amber-800"
                      }`}
                    >
                      {sc.status}
                    </span>
                  </div>
                </div>

                {/* Lyrics / Dialogue Section */}
                <div className="space-y-1">
                  <span className="text-[10px] font-bold text-[#86868B] uppercase tracking-wider flex items-center gap-1">
                    🎵 Audio Lyrics / Subtitle
                  </span>
                  <div className="p-2 bg-white rounded-xl border border-[#EDEDF0] text-xs font-semibold text-[#1D1D1F] italic">
                    &ldquo;{sc.lyrics || sc.dialogue || "Instrumental animation cue"}&rdquo;
                  </div>
                </div>

                {/* 🎬 Dedicated Video Generation Prompt Box */}
                <div className="space-y-1.5 bg-gradient-to-br from-amber-50/70 to-orange-50/70 border border-amber-200/90 rounded-xl p-3">
                  <div className="flex items-center justify-between gap-1">
                    <div className="flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-orange-600 shrink-0" />
                      <span className="text-[10px] font-extrabold text-orange-900 uppercase tracking-wider">
                        3D Video Prompt
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleCopyVideoPrompt(sc)}
                      className="inline-flex items-center gap-1 px-2.5 py-1 text-[10px] font-bold rounded-lg bg-white hover:bg-orange-500 hover:text-white text-orange-700 border border-orange-200 shadow-2xs transition-all cursor-pointer"
                      title="Copy prompt for Luma / Kling / Seedance / Runway"
                    >
                      {isPromptCopied ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-600" />
                          <span className="text-emerald-700">Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3 text-orange-600" />
                          <span>Copy Prompt</span>
                        </>
                      )}
                    </button>
                  </div>

                  <p className="text-[11px] font-normal text-neutral-800 bg-white/90 p-2.5 rounded-lg border border-amber-100 leading-relaxed max-h-32 overflow-y-auto select-all">
                    {videoPrompt}
                  </p>
                </div>

                {/* Visual Parameters */}
                <div className="space-y-1.5 text-[11px] text-[#6E6E73] pt-0.5">
                  <div className="flex items-center gap-1.5">
                    <Users2 className="w-3.5 h-3.5 text-[#86868B] shrink-0" />
                    <span className="truncate font-medium">
                      {Array.isArray(sc.characters)
                        ? sc.characters
                            .map((c: any) => (typeof c === "object" ? c.name || c.character_id : c))
                            .join(", ")
                        : sc.characters || "Lead Character"}
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5">
                    <Camera className="w-3.5 h-3.5 text-[#86868B] shrink-0" />
                    <span className="truncate font-medium">
                      {typeof sc.camera === "object" && sc.camera
                        ? `${sc.camera.shot || "wide"} • ${sc.camera.movement || "tracking"}`
                        : "Standard Camera"}
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5">
                    <Tv className="w-3.5 h-3.5 text-[#86868B] shrink-0" />
                    <span className="truncate font-medium">
                      {typeof sc.environment === "object" && sc.environment !== null
                        ? (sc.environment as any).name || (sc.environment as any).id || "Preschool Meadow"
                        : String(sc.environment || "Preschool Meadow")}
                    </span>
                  </div>
                </div>
              </div>

              {/* Rerender Scene Button */}
              <div className="pt-2 border-t border-[#EDEDF0] flex items-center justify-between gap-2">
                <button
                  onClick={() => handleRerender(sc.id, sc.scene_number)}
                  disabled={isRendering}
                  className="w-full inline-flex items-center justify-center gap-1.5 bg-white hover:bg-orange-50 hover:text-[#FF6B00] text-[#1D1D1F] border border-[#E5E5EA] text-[11px] font-bold py-2 rounded-xl transition-all cursor-pointer disabled:opacity-50"
                >
                  {isRendering ? (
                    <>
                      <Loader2 className="w-3 h-3 animate-spin" />
                      <span>Re-rendering...</span>
                    </>
                  ) : (
                    <>
                      <RotateCcw className="w-3 h-3" />
                      <span>Re-render Scene {sc.scene_number}</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* ───────────────────────────────────────────────────────────── */}
      {/* MANUAL WORKFLOW: VIDEO UPLOAD, SEQUENCE & ASSEMBLY          */}
      {/* ───────────────────────────────────────────────────────────── */}
      <div className="pt-6 border-t border-[#E5E5EA] space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-[#E5E5EA]">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-indigo-50 text-indigo-800 border border-indigo-200">
              <UploadCloud className="w-3.5 h-3.5 text-indigo-600" />
              <span>Step 6 to 8 • Upload External AI Videos & Assemble</span>
            </div>
            <h3 className="text-base font-bold text-[#1D1D1F]">
              Upload Generated Scene Videos & Assemble Final Video
            </h3>
            <p className="text-xs text-[#6E6E73]">
              Generated scenes in Google Flow / Kling / Runway? Upload your MP4/MOV clips here for automatic FFmpeg assembly.
            </p>
          </div>

        {/* Persistent status badge */}
          <div className="flex items-center gap-2">
            {scenes.length > 0 && scenes.every(s => !!s.uploaded_file) ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-2xs">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>{scenes.filter(s => !!s.uploaded_file).length}/{scenes.length} Uploaded (100% Ready)</span>
              </span>
            ) : scenes.some(s => !!s.uploaded_file) ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-amber-100 text-amber-900 border border-amber-300 shadow-2xs">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span>{scenes.filter(s => !!s.uploaded_file).length}/{scenes.length} Uploaded ({scenes.filter(s => !s.uploaded_file).length} Missing)</span>
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-700 border border-slate-200">
                <Upload className="w-4 h-4 text-slate-500" />
                <span>0/{scenes.length} Uploaded</span>
              </span>
            )}
          </div>
        </div>

        {/* Real-time Scene Slot Occupancy Ribbon */}
        {scenes.length > 0 && (
          <div className={`rounded-2xl p-4 border transition-all ${
            scenes.every(s => !!s.uploaded_file)
              ? "bg-emerald-50/70 border-emerald-300 text-emerald-950 shadow-2xs"
              : scenes.some(s => !!s.uploaded_file)
              ? "bg-amber-50/70 border-amber-300 text-amber-950"
              : "bg-slate-50 border-slate-200 text-slate-700"
          }`}>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2.5 border-b border-black/5 text-xs">
              <span className="font-bold flex items-center gap-1.5">
                <ListOrdered className="w-4 h-4 text-indigo-600" />
                <span>Scene Video Slots ({scenes.filter(s => !!s.uploaded_file).length}/{scenes.length} Assigned)</span>
              </span>
              <span className="text-[11px] font-bold">
                {scenes.every(s => !!s.uploaded_file)
                  ? "🎉 All scene slots have video clips assigned! Ready for final assembly below."
                  : `⚠️ ${scenes.filter(s => !s.uploaded_file).length} scene slot(s) missing video files: Scenes ${scenes.filter(s => !s.uploaded_file).map(s => String(s.scene_number).padStart(2, "0")).join(", ")}`}
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-9 gap-2.5 pt-3">
              {scenes.map((s) => {
                const hasFile = !!s.uploaded_file;
                const fileName = s.uploaded_file ? s.uploaded_file.split("/").pop() : null;
                const dur = s.uploaded_duration || s.duration || 0;
                return (
                  <div
                    key={s.id}
                    title={hasFile ? `Scene ${s.scene_number}: Assigned (${fileName} - ${dur.toFixed(1)}s)` : `Scene ${s.scene_number}: Vacant - upload or assign video clip`}
                    className={`p-2.5 rounded-xl text-center flex flex-col items-center justify-between gap-1.5 border-2 transition-all min-h-[76px] ${
                      hasFile
                        ? "bg-white border-emerald-500 text-emerald-950 shadow-xs"
                        : "bg-amber-50/60 border-dashed border-amber-400 text-amber-900"
                    }`}
                  >
                    <div className="flex items-center justify-between w-full">
                      <span className="text-[11px] font-black tracking-tight">
                        Scene {String(s.scene_number).padStart(2, "0")}
                      </span>
                      {hasFile ? (
                        <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[9px] font-black bg-emerald-100 text-emerald-800 border border-emerald-300">
                          <Check className="w-2.5 h-2.5 text-emerald-600" />
                          <span>Ready</span>
                        </span>
                      ) : (
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-extrabold bg-amber-100 text-amber-800 border border-amber-300">
                          ⚡ Vacant
                        </span>
                      )}
                    </div>
                    {hasFile ? (
                      <div className="w-full flex flex-col items-center">
                        <span className="text-[10px] font-mono font-bold text-slate-700 truncate w-full" title={fileName || ""}>
                          🎬 {fileName}
                        </span>
                        <span className="text-[9px] font-semibold text-emerald-700">
                          ⏱️ {dur.toFixed(1)}s
                        </span>
                      </div>
                    ) : (
                      <div className="w-full text-center">
                        <span className="text-[10px] font-medium text-amber-700 block">
                          No Video
                        </span>
                        <span className="text-[9px] text-amber-500">
                          Slot empty
                        </span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Drag & Drop Box */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={async (e) => {
            e.preventDefault();
            setDragOver(false);
            if (!e.dataTransfer.files || !projectId) return;
            setUploadingVideos(true);
            try {
              const res = await api.batchUploadScenes(projectId, Array.from(e.dataTransfer.files));
              setUnresolved(res.unresolved || []);
              const [updated, st, readyData] = await Promise.all([
                api.getScenes(projectId),
                api.getCopyStatus(projectId),
                api.checkAssemblyReadiness(projectId).catch(() => null),
              ]);
              if (onScenesUpdated) onScenesUpdated(updated);
              setCopyStatus(st);
            } catch (err: any) {
              alert("Upload failed: " + (err?.message || err));
            } finally {
              setUploadingVideos(false);
            }
          }}
          className={`border-2 border-dashed rounded-3xl p-6 text-center transition-all ${
            dragOver ? "border-[#FF6B00] bg-orange-50/50" : "border-[#E5E5EA] bg-[#FAFAFC] hover:border-[#FF6B00]/60"
          }`}
        >
          <input
            type="file"
            id="storyboard-video-upload"
            multiple
            accept="video/mp4,video/quicktime,video/webm"
            className="hidden"
            onChange={async (e) => {
              if (!e.target.files || !projectId) return;
              setUploadingVideos(true);
              try {
                const res = await api.batchUploadScenes(projectId, Array.from(e.target.files));
                setUnresolved(res.unresolved || []);
                const updated = await api.getScenes(projectId);
                if (onScenesUpdated) onScenesUpdated(updated);
                const st = await api.getCopyStatus(projectId);
                setCopyStatus(st);
              } catch (err: any) {
                alert("Upload failed: " + (err?.message || err));
              } finally {
                setUploadingVideos(false);
              }
            }}
          />
          <div className="space-y-2">
            <UploadCloud className="w-8 h-8 text-indigo-600 mx-auto" />
            <p className="text-xs font-bold text-[#1D1D1F]">
              {uploadingVideos ? "Uploading & validating video durations…" : "Drag & drop scene video files here (or click to browse)"}
            </p>
            <p className="text-[11px] text-[#86868B]">
              Files named <code>scene_01.mp4</code> or <code>01.mp4</code> automatically map to the matching scene.
            </p>
            <label
              htmlFor="storyboard-video-upload"
              className="inline-block px-4 py-2 bg-[#FF6B00] hover:bg-[#EA580C] text-white rounded-xl text-xs font-bold transition-all cursor-pointer"
            >
              Browse Files
            </label>
          </div>
        </div>

        {/* Unresolved files smart AI matching & assignment */}
        {unresolved.length > 0 && (
          <div className="bg-gradient-to-br from-indigo-50/70 via-orange-50/50 to-amber-50/80 border border-orange-200/80 rounded-2xl p-4 space-y-3.5 shadow-2xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-2 border-b border-orange-200/50">
              <div className="space-y-0.5">
                <p className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-[#FF6B00]" />
                  <span>AI Scene Matcher ({unresolved.length} clips uploaded)</span>
                </p>
                <p className="text-[11px] text-[#6E6E73]">
                  AI automatically matches video titles and keywords with each scene's visual prompt &amp; lyrics.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleRunAiMatch}
                  disabled={aiMatching}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-xs transition-all cursor-pointer disabled:opacity-50"
                  title="Run AI to compare filenames against scene prompts and generate recommendations"
                >
                  {aiMatching ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                  <span>{aiMatching ? "Matching with AI…" : "Re-Match with AI"}</span>
                </button>
                <button
                  type="button"
                  onClick={handleAutoAssignAll}
                  disabled={autoAssigning}
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-gradient-to-r from-orange-500 to-amber-600 hover:opacity-90 text-white rounded-xl text-xs font-bold shadow-xs transition-all cursor-pointer disabled:opacity-50"
                >
                  {autoAssigning ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                  <span>{autoAssigning ? "Assigning..." : "⚡ Apply AI Matches (Assign All)"}</span>
                </button>
              </div>
            </div>

            {/* Scene Occupancy Tracker Ribbon */}
            <div className="bg-white/80 border border-orange-200/60 rounded-xl p-3 space-y-2">
              <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                <span className="font-bold text-[#1D1D1F] flex items-center gap-1.5">
                  <ListOrdered className="w-3.5 h-3.5 text-indigo-600" />
                  Scene Slot Status ({scenes.filter((s) => !!s.uploaded_file).length}/{scenes.length} Assigned • {scenes.filter((s) => !s.uploaded_file).length} Vacant)
                </span>
                <span className="text-[11px] text-[#6E6E73]">
                  ⚡ Vacant slots are prioritized for new clips
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {scenes.map((s) => {
                  const isAssigned = !!s.uploaded_file;
                  const cleanFileName = s.uploaded_file ? s.uploaded_file.split("/").pop() : null;
                  return (
                    <span
                      key={s.scene_number}
                      title={isAssigned ? `Scene ${s.scene_number}: Assigned (${cleanFileName})` : `Scene ${s.scene_number}: Vacant / No Video Clip`}
                      className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all ${
                        isAssigned
                          ? "bg-emerald-50 text-emerald-800 border border-emerald-300"
                          : "bg-amber-50 text-amber-800 border border-dashed border-amber-300"
                      }`}
                    >
                      <span>Scene {String(s.scene_number).padStart(2, "0")}</span>
                      {isAssigned ? (
                        <span className="text-emerald-600 font-extrabold text-[10px]">✓ Assigned</span>
                      ) : (
                        <span className="text-amber-600 font-extrabold text-[10px]">⚡ Vacant</span>
                      )}
                    </span>
                  );
                })}
              </div>
            </div>

            <div className="space-y-2.5">
              {unresolved.map((u, i) => {
                const selectedTarget = fileSceneMap[u.tmp_path] ?? u.suggested_scene_number ?? (i + 1);
                const matchedScene = scenes.find((s) => s.scene_number === selectedTarget);
                const confidence = u.confidence ?? 50;
                const isTargetAssigned = !!matchedScene?.uploaded_file;
                const vacantScenes = scenes.filter((s) => !s.uploaded_file);
                const assignedScenes = scenes.filter((s) => !!s.uploaded_file);

                return (
                  <div
                    key={u.tmp_path || i}
                    className="flex flex-col gap-2 bg-white/90 backdrop-blur-xs border border-orange-200/70 rounded-xl p-3 text-xs shadow-2xs hover:border-orange-300 transition-all"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div className="flex items-center gap-2 min-w-0">
                        <Film className="w-4 h-4 text-indigo-600 shrink-0" />
                        <span className="font-mono text-[#1D1D1F] font-semibold truncate max-w-sm" title={u.filename}>
                          {u.filename}
                        </span>
                        {u.duration && (
                          <span className="text-[10px] bg-gray-100 text-gray-700 px-1.5 py-0.5 rounded font-mono shrink-0">
                            {u.duration.toFixed(1)}s
                          </span>
                        )}
                        {u.confidence && (
                          <span
                            className={`text-[10px] px-2 py-0.5 rounded-full font-bold flex items-center gap-1 shrink-0 ${
                              confidence >= 80
                                ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                                : confidence >= 50
                                ? "bg-amber-100 text-amber-800 border border-amber-200"
                                : "bg-gray-100 text-gray-700 border border-gray-200"
                            }`}
                          >
                            <Sparkles className="w-2.5 h-2.5" />
                            {confidence >= 80 ? "High Match" : "Match"} ({Math.round(confidence)}%)
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        <div className="flex flex-col items-end gap-0.5">
                          <div className="flex items-center gap-1.5">
                            <span className="text-[#86868B] text-[11px] font-medium">Assign to:</span>
                            <select
                              value={selectedTarget}
                              onChange={(e) => {
                                const val = Number(e.target.value);
                                setFileSceneMap((prev) => ({ ...prev, [u.tmp_path]: val }));
                              }}
                              className={`border rounded-lg px-2.5 py-1 font-bold text-xs bg-white focus:outline-none shadow-2xs ${
                                isTargetAssigned ? "border-amber-400 text-amber-900 bg-amber-50/40" : "border-[#E5E5EA] text-[#1D1D1F]"
                              }`}
                            >
                              {vacantScenes.length > 0 && (
                                <optgroup label="⚡ Vacant / Empty Scenes (Recommended)">
                                  {vacantScenes.map((s) => (
                                    <option key={s.scene_number} value={s.scene_number}>
                                      ⚡ Scene {String(s.scene_number).padStart(2, "0")} • Empty (Needs video)
                                    </option>
                                  ))}
                                </optgroup>
                              )}
                              {assignedScenes.length > 0 && (
                                <optgroup label="✓ Already Assigned Scenes (Will Overwrite)">
                                  {assignedScenes.map((s) => {
                                    const baseName = s.uploaded_file ? s.uploaded_file.split("/").pop() : "";
                                    return (
                                      <option key={s.scene_number} value={s.scene_number}>
                                        ✓ Scene {String(s.scene_number).padStart(2, "0")} • Assigned: {baseName ? baseName.slice(0, 20) : "video"}
                                      </option>
                                    );
                                  })}
                                </optgroup>
                              )}
                            </select>
                          </div>
                          {isTargetAssigned ? (
                            <span className="text-[10px] font-semibold text-amber-700">
                              ⚠️ Replaces video in Scene {selectedTarget}
                            </span>
                          ) : (
                            <span className="text-[10px] font-semibold text-emerald-700">
                              ⚡ Slot is vacant
                            </span>
                          )}
                        </div>
                        <button
                          type="button"
                          onClick={async () => {
                            try {
                              await api.assignUnresolvedVideo(projectId, selectedTarget, u.tmp_path);
                              setUnresolved((prev) => prev.filter((x) => x.tmp_path !== u.tmp_path));
                              const updated = await api.getScenes(projectId);
                              if (onScenesUpdated) onScenesUpdated(updated);
                              const st = await api.getCopyStatus(projectId);
                              setCopyStatus(st);
                            } catch (err: any) {
                              alert("Assignment failed: " + err.message);
                            }
                          }}
                          className="px-3.5 py-1.5 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-bold text-xs transition-colors cursor-pointer shadow-2xs"
                        >
                          Assign
                        </button>
                      </div>
                    </div>

                    {/* AI Explanation and Prompt Preview */}
                    {(u.match_reason || (matchedScene && (matchedScene.video_prompt || matchedScene.lyrics))) && (
                      <div className="bg-slate-50 border border-slate-100 rounded-lg p-2 text-[11px] space-y-1">
                        {u.match_reason && (
                          <p className="text-indigo-900 font-medium flex items-center gap-1.5">
                            <span className="font-bold text-indigo-700">AI Reason:</span> {u.match_reason}
                          </p>
                        )}
                        {matchedScene && (matchedScene.video_prompt || matchedScene.lyrics) && (
                          <p className="text-[#6E6E73] truncate">
                            <span className="font-semibold text-[#1D1D1F]">Scene {matchedScene.scene_number} Target Prompt:</span>{" "}
                            {matchedScene.lyrics ? `"${matchedScene.lyrics}" • ` : ""}{matchedScene.video_prompt || ""}
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Sequence and Assembly Controls */}
        {(() => {
          const missingScenes = scenes.filter(s => !s.uploaded_file);
          const allReady = missingScenes.length === 0 && scenes.length > 0;
          return (
            <div className="space-y-3">
              {/* Missing validation banner */}
              {!allReady && scenes.length > 0 && (
                <div className="flex flex-col gap-1.5 p-4 bg-red-50 border-2 border-red-300 rounded-2xl">
                  <div className="flex items-center gap-2 text-sm font-bold text-red-900">
                    <AlertTriangle className="w-4 h-4 text-red-600 flex-shrink-0" />
                    <span>⛔ Cannot Assemble — {missingScenes.length} of {scenes.length} scene{missingScenes.length !== 1 ? "s" : ""} missing video clips</span>
                  </div>
                  <p className="text-xs text-red-700">
                    Upload or assign video files to all scene slots before assembling.
                    Missing: Scenes {missingScenes.map(s => String(s.scene_number).padStart(2, "0")).join(", ")}
                  </p>
                </div>
              )}

              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 bg-[#FAFAFC] border border-[#E5E5EA] rounded-2xl">
                <div className="flex items-center gap-2 text-xs">
                  <ListOrdered className="w-4 h-4 text-cyan-600" />
                  <span className="font-bold text-[#1D1D1F]">Sequence Order:</span>
                  <span className="font-mono text-[#6E6E73]">
                    {scenes.map(s => String(s.scene_number).padStart(2, "0")).join(" → ")}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={async () => {
                      setConfirmingSequence(true);
                      try {
                        const order = scenes.map(s => s.scene_number).sort((a, b) => a - b);
                        await api.confirmSceneSequence(projectId, order);
                        setSequenceConfirmed(true);
                      } catch (err: any) {
                        alert("Failed to confirm: " + err.message);
                      } finally {
                        setConfirmingSequence(false);
                      }
                    }}
                    disabled={confirmingSequence || scenes.length === 0}
                    className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
                      sequenceConfirmed ? "bg-emerald-600 text-white" : "bg-cyan-600 hover:bg-cyan-700 text-white"
                    }`}
                  >
                    {sequenceConfirmed ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Check className="w-3.5 h-3.5" />}
                    <span>{sequenceConfirmed ? "Sequence Confirmed ✓" : "Confirm Sequence"}</span>
                  </button>

                  <div className="relative group">
                    <button
                      onClick={async () => {
                        setAssembling(true);
                        setAssembleError(null);
                        try {
                          const res = await api.generateFinalVideoFromUploads(projectId);
                          setFinalVideoResult(res);
                          if (onSceneRerendered) onSceneRerendered();
                        } catch (err: any) {
                          setAssembleError(err?.message || "Assembly failed");
                        } finally {
                          setAssembling(false);
                        }
                      }}
                      disabled={assembling || !allReady}
                      title={!allReady ? `Cannot assemble: ${missingScenes.length} scene(s) still missing video clips` : "Assemble final video"}
                      className={`px-5 py-2 rounded-xl text-xs font-extrabold transition-all flex items-center gap-2 ${
                        allReady
                          ? "bg-gradient-to-r from-emerald-600 to-green-600 hover:opacity-95 text-white shadow-md shadow-emerald-500/20 cursor-pointer"
                          : "bg-slate-200 text-slate-400 cursor-not-allowed opacity-60"
                      }`}
                    >
                      {assembling ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Film className="w-3.5 h-3.5" />}
                      <span>{assembling ? "Assembling FFmpeg Video…" : "Assemble Final Video"}</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })()}

        {/* Assemble error */}
        {assembleError && (
          <div className="p-3.5 bg-red-50 border border-red-200 rounded-xl text-xs text-red-800">
            <strong>Error:</strong> {assembleError}
          </div>
        )}

        {/* Final Video player result & High-CTR Thumbnail */}
        {finalVideoResult && (
          <div className="bg-emerald-50/50 border border-emerald-300 rounded-3xl p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-emerald-200 pb-3">
              <span className="text-xs font-bold text-emerald-900 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Final Video Assembled Successfully ({finalVideoResult.duration?.toFixed(1)}s)
              </span>
              <div className="flex items-center gap-2">
                <a
                  href={`${API_BASE}/api/v1/projects/${projectId}/thumbnail?t=${Date.now()}`}
                  download="thumbnail.jpg"
                  target="_blank"
                  rel="noreferrer"
                  className="px-3 py-1.5 bg-orange-50 hover:bg-orange-100 border border-orange-200 text-[#FF6B00] rounded-xl text-xs font-bold flex items-center gap-1"
                >
                  <ImageIcon className="w-3.5 h-3.5" />
                  <span>Download Thumbnail</span>
                </a>
                <a
                  href={`${API_BASE}/api/v1/projects/${projectId}/assembly/final-video`}
                  download="final_kids_song.mp4"
                  className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold flex items-center gap-1"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download MP4</span>
                </a>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
              <div className="aspect-video bg-black rounded-2xl overflow-hidden shadow-md">
                <video
                  src={`${API_BASE}/api/v1/projects/${projectId}/assembly/final-video?t=${Date.now()}`}
                  controls
                  playsInline
                  className="w-full h-full"
                />
              </div>
              <div className="relative aspect-video rounded-2xl overflow-hidden bg-slate-900 border border-[#E5E5EA] shadow-md group">
                <img
                  src={`${API_BASE}/api/v1/projects/${projectId}/thumbnail?t=${Date.now()}`}
                  alt="High-CTR YouTube Cover"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src =
                      "https://placehold.co/1280x720/1e293b/f8fafc?text=High-CTR+Thumbnail+Ready";
                  }}
                />
                <div className="absolute top-2 left-2 px-2 py-0.5 rounded-full bg-red-600/90 text-white text-[10px] font-black uppercase tracking-wider backdrop-blur-xs">
                  🔥 HIGH CTR / HIGH CPM
                </div>
                <div className="absolute bottom-2 right-2 px-2 py-0.5 rounded-md bg-black/80 text-white text-[10px] font-bold backdrop-blur-xs">
                  16:9 • 1280x720
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
