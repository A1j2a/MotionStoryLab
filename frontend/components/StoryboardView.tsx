"use client";

import { useState, useEffect } from "react";
import { Scene, AISettings } from "@/lib/types";
import { api } from "@/lib/api";
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

  useEffect(() => {
    api.getAISettings().then(setAiSettings).catch(() => {});
  }, []);

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

  const handleCopyVideoPrompt = (sc: Scene) => {
    const prompt = getVideoPrompt(sc);
    navigator.clipboard.writeText(prompt);
    setCopiedPromptId(sc.id);
    setTimeout(() => setCopiedPromptId(null), 2000);
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
    </div>
  );
}
