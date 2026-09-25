"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { api } from "@/lib/api";
import { Project, Scene, AudioTimeline } from "@/lib/types";
import {
  Sparkles,
  CheckCircle2,
  Copy,
  Check,
  Film,
  UploadCloud,
  Clapperboard,
  Music,
  Clock,
  Play,
  Pause,
  RefreshCw,
  AlertTriangle,
  ChevronDown,
  Layers,
  ArrowRight,
  Download,
  Loader2,
  FileVideo,
  ListOrdered,
  X,
  ExternalLink,
  PlusCircle,
  Hash,
  FileText,
  AlignLeft,
} from "lucide-react";

interface ManualWorkflowViewProps {
  initialProjectId?: string;
  onProjectChange?: (projectId: string) => void;
}

type PromptStatus = "NOT_COPIED" | "PROMPT_COPIED" | "VIDEO_UPLOADED" | "ORDER_CONFIRMED" | "FAILED";

interface SceneWithStatus extends Scene {
  prompt_status?: PromptStatus;
  prompt_copied_at?: string | null;
  uploaded_file?: string | null;
  uploaded_duration?: number | null;
  scene_order?: number;
}

interface SeoPackage {
  title: string;
  description: string;
  tags: string;
  caption: string;
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

export function ManualWorkflowView({ initialProjectId, onProjectChange }: ManualWorkflowViewProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>(initialProjectId || "");
  const [activeProject, setActiveProject] = useState<Project | null>(null);

  // Step 1: Topic Selection & AI Ideas
  const [topicInput, setTopicInput] = useState<string>("");
  const [aiTopics, setAiTopics] = useState<any[]>([]);
  const [loadingAiTopics, setLoadingAiTopics] = useState<boolean>(false);
  const [creatingProject, setCreatingProject] = useState<boolean>(false);

  // Step 2: SEO Content
  const [seoPkg, setSeoPkg] = useState<SeoPackage | null>(null);
  const [loadingSeo, setLoadingSeo] = useState<boolean>(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  // Step 3 & 4: Audio & SRT
  const [audioTimeline, setAudioTimeline] = useState<AudioTimeline | null>(null);
  const [generatingAudio, setGeneratingAudio] = useState<boolean>(false);
  const [uploadingAudio, setUploadingAudio] = useState<boolean>(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState<boolean>(false);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const audioFileInputRef = useRef<HTMLInputElement | null>(null);

  // Step 5: Scene Planning & Duration Setting
  const [targetDuration, setTargetDuration] = useState<number>(8);
  const [scenes, setScenes] = useState<SceneWithStatus[]>([]);
  const [planningScenes, setPlanningScenes] = useState<boolean>(false);

  // Step 6-9: Copy Tracking
  const [copyStatus, setCopyStatus] = useState<{ total_scenes: number; copied_count: number; uploaded_count: number } | null>(null);
  const [justCopiedSceneId, setJustCopiedSceneId] = useState<string | null>(null);
  const [expandedSceneId, setExpandedSceneId] = useState<string | null>(null);

  // Step 10-12: Upload & Mapping
  const [uploadingVideos, setUploadingVideos] = useState<boolean>(false);
  const [dragOver, setDragOver] = useState<boolean>(false);
  const [uploadResults, setUploadResults] = useState<UploadResult[]>([]);
  const [unresolved, setUnresolved] = useState<UnresolvedFile[]>([]);
  const [assigningFile, setAssigningFile] = useState<UnresolvedFile | null>(null);
  const [assignTargetScene, setAssignTargetScene] = useState<number>(1);
  const videoFileInputRef = useRef<HTMLInputElement | null>(null);

  // Step 13-14: Sequence Confirmation
  const [sequenceOrder, setSequenceOrder] = useState<number[]>([]);
  const [sequenceConfirmed, setSequenceConfirmed] = useState<boolean>(false);
  const [confirmingSequence, setConfirmingSequence] = useState<boolean>(false);

  // Step 15-16: Assembly & Final Video
  const [readiness, setReadiness] = useState<AssemblyReadiness | null>(null);
  const [checkingReadiness, setCheckingReadiness] = useState<boolean>(false);
  const [assembling, setAssembling] = useState<boolean>(false);
  const [finalVideoResult, setFinalVideoResult] = useState<{ status: string; final_video: string; duration: number } | null>(null);
  const [assembleError, setAssembleError] = useState<string | null>(null);

  // Fetch Projects List
  const loadProjects = useCallback(async () => {
    try {
      const list = await api.getProjects();
      setProjects(list || []);
      if (!selectedProjectId && list && list.length > 0) {
        setSelectedProjectId(list[0].id);
        if (onProjectChange) onProjectChange(list[0].id);
      }
    } catch (e) {
      console.error("Failed to load projects:", e);
    }
  }, [selectedProjectId, onProjectChange]);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  // Load project-specific data whenever selectedProjectId changes
  const loadProjectData = useCallback(async (projId: string) => {
    if (!projId) return;
    try {
      const proj = await api.getProject(projId);
      setActiveProject(proj);
      if (proj.topic) setTopicInput(proj.topic);

      // Load SEO, Audio timeline, Scenes, Copy Status in parallel
      const [seoData, timeline, scenesList, statusData] = await Promise.all([
        api.getManualSeo(projId).catch(() => null),
        api.getAudioTimeline(projId).catch(() => null),
        api.getScenes(projId).catch(() => []),
        api.getCopyStatus(projId).catch(() => null),
      ]);

      if (seoData) setSeoPkg(seoData);
      if (timeline) setAudioTimeline(timeline);
      if (scenesList) {
        setScenes(scenesList as SceneWithStatus[]);
        setSequenceOrder(scenesList.map((s: Scene) => s.scene_number).sort((a: number, b: number) => a - b));
        const allConfirmed = scenesList.length > 0 && scenesList.every((s: SceneWithStatus) => s.prompt_status === "ORDER_CONFIRMED");
        setSequenceConfirmed(allConfirmed);
      }
      if (statusData) setCopyStatus(statusData);
    } catch (e) {
      console.error("Failed to load project details:", e);
    }
  }, []);

  useEffect(() => {
    if (selectedProjectId) {
      loadProjectData(selectedProjectId);
    }
  }, [selectedProjectId, loadProjectData]);

  // Copy helper
  const copyToClipboard = async (text: string, key: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedKey(key);
      setTimeout(() => setCopiedKey(null), 2000);
    } catch (e) {
      console.error("Clipboard copy failed:", e);
    }
  };

  // Step 1 Actions: Generate AI Topics & Select/Create Project
  const handleGenerateAiTopics = async () => {
    setLoadingAiTopics(true);
    try {
      const dynamicTopics = await api.discoverTopics({ limit: 6 });
      setAiTopics(dynamicTopics || []);
    } catch (e) {
      console.error("Failed to fetch AI topics:", e);
    } finally {
      setLoadingAiTopics(false);
    }
  };

  const handleSelectOrCreateTopic = async (topicTitle: string) => {
    if (!topicTitle.trim()) return;
    setTopicInput(topicTitle);
    setCreatingProject(true);
    try {
      // Create new project with this topic
      const newProj = await api.createProject({
        title: topicTitle,
        topic: topicTitle,
        target_age: "Preschool (2-5 Years)",
        duration_min: 2,
      });
      await loadProjects();
      setSelectedProjectId(newProj.id);
      if (onProjectChange) onProjectChange(newProj.id);

      // Auto-trigger SEO generation for the new project
      setLoadingSeo(true);
      const seo = await api.generateManualSeo(newProj.id, topicTitle);
      setSeoPkg(seo);
    } catch (e) {
      console.error("Failed to create project with topic:", e);
    } finally {
      setCreatingProject(false);
      setLoadingSeo(false);
    }
  };

  // Step 2 Actions: Generate SEO
  const handleGenerateSeo = async () => {
    if (!selectedProjectId) return;
    setLoadingSeo(true);
    try {
      const seo = await api.generateManualSeo(selectedProjectId, topicInput);
      setSeoPkg(seo);
    } catch (e) {
      console.error("Failed to generate SEO:", e);
    } finally {
      setLoadingSeo(false);
    }
  };

  // Step 3 Actions: Generate Neural Audio or Upload
  const handleGenerateAudio = async () => {
    if (!selectedProjectId) return;
    setGeneratingAudio(true);
    try {
      const timeline = await api.generateNeuralAudio(selectedProjectId);
      setAudioTimeline(timeline);
    } catch (e) {
      console.error("Audio generation failed:", e);
      alert("Audio generation failed. Ensure neural voice service is active.");
    } finally {
      setGeneratingAudio(false);
    }
  };

  const handleAudioUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !selectedProjectId) return;
    setUploadingAudio(true);
    try {
      const timeline = await api.uploadAudioFile(selectedProjectId, file);
      setAudioTimeline(timeline);
    } catch (err: any) {
      alert("Audio upload failed: " + (err?.message || err));
    } finally {
      setUploadingAudio(false);
    }
  };

  const toggleAudioPlay = () => {
    if (!audioPlayerRef.current) return;
    if (isPlayingAudio) {
      audioPlayerRef.current.pause();
      setIsPlayingAudio(false);
    } else {
      audioPlayerRef.current.play().then(() => setIsPlayingAudio(true)).catch(() => {});
    }
  };

  // Step 5 Actions: Generate Scene Plan
  const handlePlanScenes = async () => {
    if (!selectedProjectId) return;
    setPlanningScenes(true);
    try {
      const newScenes = await api.generateStoryboard(selectedProjectId, targetDuration);
      setScenes(newScenes as SceneWithStatus[]);
      setSequenceOrder(newScenes.map((s: Scene) => s.scene_number).sort((a: number, b: number) => a - b));
      const statusData = await api.getCopyStatus(selectedProjectId);
      setCopyStatus(statusData);
    } catch (err: any) {
      console.error("Storyboard generation failed:", err);
      alert("Failed to plan scenes: " + (err?.message || err));
    } finally {
      setPlanningScenes(false);
    }
  };

  // Step 6-9 Actions: Mark Scene Copied
  const handleCopyScenePrompt = async (scene: SceneWithStatus) => {
    if (!selectedProjectId) return;
    const promptText = scene.video_prompt || scene.dialogue || `Scene ${scene.scene_number}: ${scene.lyrics || ""}`;
    await copyToClipboard(promptText, `scene_${scene.id}`);
    setJustCopiedSceneId(scene.id);
    setTimeout(() => setJustCopiedSceneId(null), 2000);

    try {
      await api.markSceneCopied(selectedProjectId, scene.id);
      setScenes((prev) =>
        prev.map((s) => (s.id === scene.id ? { ...s, prompt_status: "PROMPT_COPIED" as PromptStatus } : s))
      );
      setCopyStatus((prev) => (prev ? { ...prev, copied_count: prev.copied_count + 1 } : prev));
    } catch (e) {
      console.error("Failed to mark scene copied:", e);
    }
  };

  // Step 10-12 Actions: Batch Upload Videos
  const handleBatchUpload = async (files: FileList | null) => {
    if (!files || !selectedProjectId) return;
    setUploadingVideos(true);
    try {
      const res = await api.batchUploadScenes(selectedProjectId, Array.from(files));
      setUploadResults(res.results || []);
      setUnresolved(res.unresolved || []);
      // Reload scenes & status
      const [updatedScenes, statusData] = await Promise.all([
        api.getScenes(selectedProjectId),
        api.getCopyStatus(selectedProjectId),
      ]);
      setScenes(updatedScenes as SceneWithStatus[]);
      setCopyStatus(statusData);
    } catch (err: any) {
      alert("Upload failed: " + (err?.message || err));
    } finally {
      setUploadingVideos(false);
    }
  };

  // Manual Assign Unresolved Video
  const handleAssignUnresolved = async () => {
    if (!assigningFile || !selectedProjectId) return;
    try {
      await api.assignUnresolvedVideo(selectedProjectId, assignTargetScene, assigningFile.tmp_path);
      setUnresolved((prev) => prev.filter((u) => u.tmp_path !== assigningFile.tmp_path));
      setAssigningFile(null);
      const [updatedScenes, statusData] = await Promise.all([
        api.getScenes(selectedProjectId),
        api.getCopyStatus(selectedProjectId),
      ]);
      setScenes(updatedScenes as SceneWithStatus[]);
      setCopyStatus(statusData);
    } catch (err: any) {
      alert("Assignment failed: " + (err?.message || err));
    }
  };

  // Step 14 Actions: Confirm Sequence
  const handleConfirmSequence = async () => {
    if (!selectedProjectId) return;
    setConfirmingSequence(true);
    try {
      await api.confirmSceneSequence(selectedProjectId, sequenceOrder);
      setSequenceConfirmed(true);
      const updatedScenes = await api.getScenes(selectedProjectId);
      setScenes(updatedScenes as SceneWithStatus[]);
    } catch (err: any) {
      alert("Failed to confirm sequence: " + (err?.message || err));
    } finally {
      setConfirmingSequence(false);
    }
  };

  // Step 15-16 Actions: Assembly Readiness & Final Video
  const handleCheckReadiness = async () => {
    if (!selectedProjectId) return;
    setCheckingReadiness(true);
    try {
      const r = await api.checkAssemblyReadiness(selectedProjectId);
      setReadiness(r);
    } catch (e) {
      console.error("Readiness check failed:", e);
    } finally {
      setCheckingReadiness(false);
    }
  };

  const handleGenerateFinalVideo = async () => {
    if (!selectedProjectId) return;
    setAssembling(true);
    setAssembleError(null);
    try {
      const result = await api.generateFinalVideoFromUploads(selectedProjectId);
      setFinalVideoResult(result);
    } catch (err: any) {
      setAssembleError(err?.message || "Final video assembly failed.");
    } finally {
      setAssembling(false);
    }
  };

  // Computations
  const totalScenes = scenes.length;
  const copiedCount = copyStatus?.copied_count ?? scenes.filter((s) => s.prompt_status && s.prompt_status !== "NOT_COPIED").length;
  const uploadedCount = scenes.filter((s) => s.uploaded_file).length;
  const allCopied = totalScenes > 0 && copiedCount >= totalScenes;
  const allUploaded = totalScenes > 0 && uploadedCount >= totalScenes;
  const songDuration = audioTimeline?.total_duration || 0;
  const plannedScenesCount = songDuration > 0 ? Math.ceil(songDuration / targetDuration) : 0;

  return (
    <div className="space-y-8 pb-16">
      {/* Top Banner & Project Selector */}
      <div className="bg-white border border-[#E5E5EA] rounded-3xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-[#FF6B00] via-[#FF8533] to-[#FFA366] flex items-center justify-center shadow-lg shadow-orange-500/25">
            <Film className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-extrabold uppercase tracking-widest text-[#FF6B00] bg-orange-50 border border-orange-200 px-2 py-0.5 rounded-full">
                New Workflow
              </span>
              <h2 className="text-xl font-bold text-[#1D1D1F]">
                Manual AI Scene Generation + Automatic Assembly
              </h2>
            </div>
            <p className="text-xs text-[#6E6E73] mt-0.5">
              Generate scene prompts → Copy to Google Flow / AI Video → Upload back → Auto-assemble with FFmpeg
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <p className="text-[11px] font-semibold text-[#86868B]">Current Project</p>
            <p className="text-xs font-bold text-[#1D1D1F] max-w-[200px] truncate">
              {activeProject?.title || "Select or create below"}
            </p>
          </div>
          <select
            value={selectedProjectId}
            onChange={(e) => {
              setSelectedProjectId(e.target.value);
              if (onProjectChange) onProjectChange(e.target.value);
            }}
            className="border border-[#E5E5EA] rounded-2xl px-3 py-2 text-xs font-bold text-[#1D1D1F] bg-[#FAFAFC] focus:outline-none focus:ring-2 focus:ring-[#FF6B00]/40 max-w-[220px]"
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.title || p.topic}
              </option>
            ))}
          </select>
          <button
            onClick={() => loadProjectData(selectedProjectId)}
            className="p-2 border border-[#E5E5EA] rounded-2xl hover:bg-[#F5F5F7] text-[#6E6E73] transition-colors"
            title="Refresh current project data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* ─────────────────────────────────────────────────────────────────── */}
      {/* STEP 1: TOPIC SELECTION & DYNAMIC AI DISCOVERY (NO STATIC DATA)     */}
      {/* ─────────────────────────────────────────────────────────────────── */}
      <section className="bg-white border border-[#E5E5EA] rounded-3xl p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-[#E5E5EA] pb-4">
          <div className="space-y-0.5">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-orange-50 text-[#EA580C] border border-orange-200">
              <Sparkles className="w-3.5 h-3.5 text-[#FF6B00]" />
              <span>Step 1 • Topic Selection</span>
            </div>
            <h3 className="text-lg font-bold text-[#1D1D1F]">Preschool Rhyme Topic</h3>
            <p className="text-xs text-[#6E6E73]">
              Enter any custom topic or click generate for dynamic 100% AI-researched topic opportunities.
            </p>
          </div>
          <button
            onClick={handleGenerateAiTopics}
            disabled={loadingAiTopics}
            className="flex items-center gap-1.5 px-4 py-2 bg-[#FAFAFC] border border-[#E5E5EA] hover:border-[#FF6B00] rounded-2xl text-xs font-bold text-[#1D1D1F] transition-all hover:shadow-xs"
          >
            {loadingAiTopics ? <Loader2 className="w-3.5 h-3.5 animate-spin text-[#FF6B00]" /> : <Sparkles className="w-3.5 h-3.5 text-[#FF6B00]" />}
            <span>{loadingAiTopics ? "AI Researching…" : "✨ Generate AI Topic Ideas"}</span>
          </button>
        </div>

        {/* Input Box for Custom Topic */}
        <div className="flex gap-2">
          <input
            type="text"
            value={topicInput}
            onChange={(e) => setTopicInput(e.target.value)}
            placeholder="Enter custom nursery rhyme topic (e.g. Brush Your Teeth, Five Little Monkeys)..."
            className="flex-1 border border-[#E5E5EA] rounded-2xl px-4 py-2.5 text-sm text-[#1D1D1F] bg-[#FAFAFC] focus:outline-none focus:ring-2 focus:ring-[#FF6B00]/40 font-medium"
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSelectOrCreateTopic(topicInput);
            }}
          />
          <button
            onClick={() => handleSelectOrCreateTopic(topicInput)}
            disabled={creatingProject || !topicInput.trim()}
            className="px-5 py-2.5 bg-[#FF6B00] hover:bg-[#EA580C] text-white rounded-2xl text-xs font-bold transition-all shadow-md shadow-orange-500/20 disabled:opacity-50 flex items-center gap-2"
          >
            {creatingProject ? <Loader2 className="w-4 h-4 animate-spin" /> : <PlusCircle className="w-4 h-4" />}
            <span>Use Topic & Start</span>
          </button>
        </div>

        {/* Dynamic AI Generated Topic Suggestions Cards */}
        {aiTopics.length > 0 && (
          <div className="pt-2">
            <p className="text-[11px] font-bold text-[#86868B] uppercase tracking-wider mb-2">
              Dynamic AI Suggestions (Click to Select):
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {aiTopics.map((item, idx) => (
                <div
                  key={idx}
                  onClick={() => handleSelectOrCreateTopic(item.topic || item.suggested_title)}
                  className="p-3.5 border border-[#E5E5EA] rounded-2xl bg-[#FAFAFC] hover:bg-orange-50/50 hover:border-orange-300 transition-all cursor-pointer group"
                >
                  <p className="text-xs font-bold text-[#1D1D1F] group-hover:text-[#FF6B00] line-clamp-1">
                    {item.suggested_title || item.topic}
                  </p>
                  <p className="text-[11px] text-[#6E6E73] mt-1 line-clamp-2">
                    {item.content_angle || item.suggested_story_concept || item.why_worth_considering}
                  </p>
                  <div className="mt-2 flex items-center justify-between text-[10px] text-[#86868B]">
                    <span className="font-semibold text-orange-600">{item.category}</span>
                    <span className="font-bold flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                      Select <ArrowRight className="w-3 h-3 text-[#FF6B00]" />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* ─────────────────────────────────────────────────────────────────── */}
      {/* STEP 2: SEO CONTENT (TITLE, DESCRIPTION, TAGS, CAPTION + COPY BTNS) */}
      {/* ─────────────────────────────────────────────────────────────────── */}
      <section className="bg-white border border-[#E5E5EA] rounded-3xl p-6 shadow-xs space-y-5">
        <div className="flex items-center justify-between border-b border-[#E5E5EA] pb-4">
          <div className="space-y-0.5">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-50 text-blue-800 border border-blue-200">
              <Hash className="w-3.5 h-3.5 text-blue-600" />
              <span>Step 2 • SEO Content Generation</span>
            </div>
            <h3 className="text-lg font-bold text-[#1D1D1F]">YouTube SEO Metadata Package</h3>
            <p className="text-xs text-[#6E6E73]">
              Every output has a dedicated single-click copy button (changes to Copied ✓ instantly).
            </p>
          </div>
          <button
            onClick={handleGenerateSeo}
            disabled={loadingSeo || !selectedProjectId}
            className="flex items-center gap-1.5 px-4 py-2 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-2xl text-xs font-bold text-blue-800 transition-all"
          >
            {loadingSeo ? <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-600" /> : <Sparkles className="w-3.5 h-3.5 text-blue-600" />}
            <span>{loadingSeo ? "Generating SEO…" : "Regenerate SEO"}</span>
          </button>
        </div>

        {seoPkg ? (
          <div className="space-y-4">
            {/* 1. YouTube Title */}
            <div className="bg-[#FAFAFC] border border-[#E5E5EA] rounded-2xl p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-extrabold uppercase tracking-wider text-[#6E6E73] flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-blue-600" />
                  YouTube Title
                </span>
                <button
                  onClick={() => copyToClipboard(seoPkg.title, "title")}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                    copiedKey === "title"
                      ? "bg-green-600 text-white"
                      : "bg-white border border-[#E5E5EA] text-[#1D1D1F] hover:bg-[#F5F5F7]"
                  }`}
                >
                  {copiedKey === "title" ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5 text-[#86868B]" />}
                  <span>{copiedKey === "title" ? "COPIED ✓" : "COPY"}</span>
                </button>
              </div>
              <p className="text-sm font-bold text-[#1D1D1F] bg-white border border-[#E5E5EA] rounded-xl p-3 select-all">
                {seoPkg.title}
              </p>
            </div>

            {/* 2. YouTube Description */}
            <div className="bg-[#FAFAFC] border border-[#E5E5EA] rounded-2xl p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-extrabold uppercase tracking-wider text-[#6E6E73] flex items-center gap-1.5">
                  <AlignLeft className="w-3.5 h-3.5 text-blue-600" />
                  YouTube Description
                </span>
                <button
                  onClick={() => copyToClipboard(seoPkg.description, "description")}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                    copiedKey === "description"
                      ? "bg-green-600 text-white"
                      : "bg-white border border-[#E5E5EA] text-[#1D1D1F] hover:bg-[#F5F5F7]"
                  }`}
                >
                  {copiedKey === "description" ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5 text-[#86868B]" />}
                  <span>{copiedKey === "description" ? "COPIED ✓" : "COPY"}</span>
                </button>
              </div>
              <div className="bg-white border border-[#E5E5EA] rounded-xl p-3 text-xs text-[#1D1D1F] whitespace-pre-wrap font-mono max-h-40 overflow-y-auto select-all">
                {seoPkg.description}
              </div>
            </div>

            {/* 3. YouTube Tags */}
            <div className="bg-[#FAFAFC] border border-[#E5E5EA] rounded-2xl p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-extrabold uppercase tracking-wider text-[#6E6E73] flex items-center gap-1.5">
                  <Hash className="w-3.5 h-3.5 text-blue-600" />
                  YouTube Tags
                </span>
                <button
                  onClick={() => copyToClipboard(seoPkg.tags, "tags")}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                    copiedKey === "tags"
                      ? "bg-green-600 text-white"
                      : "bg-white border border-[#E5E5EA] text-[#1D1D1F] hover:bg-[#F5F5F7]"
                  }`}
                >
                  {copiedKey === "tags" ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5 text-[#86868B]" />}
                  <span>{copiedKey === "tags" ? "COPIED ✓" : "COPY"}</span>
                </button>
              </div>
              <p className="text-xs text-[#1D1D1F] bg-white border border-[#E5E5EA] rounded-xl p-3 font-mono break-words select-all">
                {seoPkg.tags}
              </p>
            </div>

            {/* 4. YouTube Caption */}
            <div className="bg-[#FAFAFC] border border-[#E5E5EA] rounded-2xl p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-extrabold uppercase tracking-wider text-[#6E6E73] flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                  Shorts / Social Caption
                </span>
                <button
                  onClick={() => copyToClipboard(seoPkg.caption, "caption")}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                    copiedKey === "caption"
                      ? "bg-green-600 text-white"
                      : "bg-white border border-[#E5E5EA] text-[#1D1D1F] hover:bg-[#F5F5F7]"
                  }`}
                >
                  {copiedKey === "caption" ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5 text-[#86868B]" />}
                  <span>{copiedKey === "caption" ? "COPIED ✓" : "COPY"}</span>
                </button>
              </div>
              <p className="text-xs font-medium text-[#1D1D1F] bg-white border border-[#E5E5EA] rounded-xl p-3 select-all">
                {seoPkg.caption}
              </p>
            </div>
          </div>
        ) : (
          <div className="bg-[#FAFAFC] border border-dashed border-[#E5E5EA] rounded-2xl p-8 text-center space-y-3">
            <Sparkles className="w-8 h-8 text-[#FF6B00] mx-auto opacity-70" />
            <p className="text-xs text-[#86868B]">
              No SEO package generated yet. Select a topic above or click "Generate SEO".
            </p>
            <button
              onClick={handleGenerateSeo}
              disabled={loadingSeo || !selectedProjectId}
              className="px-4 py-2 bg-[#FF6B00] text-white rounded-xl text-xs font-bold hover:bg-[#EA580C] transition-all"
            >
              Generate SEO Metadata Now
            </button>
          </div>
        )}
      </section>

      {/* ─────────────────────────────────────────────────────────────────── */}
      {/* STEP 3 & 4: SONG GENERATION, AUDIO TIMELINE & SRT AUTHORITATIVE     */}
      {/* ─────────────────────────────────────────────────────────────────── */}
      <section className="bg-white border border-[#E5E5EA] rounded-3xl p-6 shadow-xs space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E5E5EA] pb-4">
          <div className="space-y-0.5">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-800 border border-amber-200">
              <Music className="w-3.5 h-3.5 text-amber-600" />
              <span>Step 3 & 4 • Song & SRT Timing Source</span>
            </div>
            <h3 className="text-lg font-bold text-[#1D1D1F]">Master Song Audio & Subtitles</h3>
            <p className="text-xs text-[#6E6E73]">
              The song and SRT timing dictate the scene plan. SRT start & end times remain authoritative.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="file"
              ref={audioFileInputRef}
              onChange={handleAudioUpload}
              accept="audio/*"
              className="hidden"
            />
            <button
              onClick={() => audioFileInputRef.current?.click()}
              disabled={uploadingAudio || !selectedProjectId}
              className="px-3.5 py-2 border border-[#E5E5EA] bg-[#FAFAFC] hover:bg-[#F5F5F7] rounded-xl text-xs font-bold text-[#1D1D1F] transition-all flex items-center gap-1.5"
            >
              <UploadCloud className="w-3.5 h-3.5 text-amber-600" />
              <span>{uploadingAudio ? "Uploading Audio…" : "Upload Audio File"}</span>
            </button>
            <button
              onClick={handleGenerateAudio}
              disabled={generatingAudio || !selectedProjectId}
              className="px-4 py-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-amber-500/20 flex items-center gap-1.5"
            >
              {generatingAudio ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Music className="w-3.5 h-3.5" />}
              <span>{generatingAudio ? "Generating Vocal Track…" : "Generate Vocal Audio"}</span>
            </button>
          </div>
        </div>

        {audioTimeline ? (
          <div className="bg-[#FAFAFC] border border-[#E5E5EA] rounded-2xl p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <button
                  onClick={toggleAudioPlay}
                  className="w-10 h-10 rounded-xl bg-amber-500 hover:bg-amber-600 text-white flex items-center justify-center transition-all shadow-md shadow-amber-500/25"
                >
                  {isPlayingAudio ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
                </button>
                <div>
                  <p className="text-xs font-bold text-[#1D1D1F]">
                    {audioTimeline.title || activeProject?.title || "Master Audio Track"}
                  </p>
                  <p className="text-[11px] text-[#86868B] flex items-center gap-1">
                    <Clock className="w-3 h-3 text-amber-600" />
                    <span>Total Duration: <strong>{audioTimeline.total_duration?.toFixed(1)}s</strong></span>
                    <span>• {audioTimeline.lyric_timestamps?.length || 0} Lyric Lines</span>
                  </p>
                </div>
              </div>

              {/* Per-Scene Target Duration Selector */}
              <div className="flex items-center gap-2 bg-white border border-[#E5E5EA] px-3.5 py-2 rounded-xl">
                <span className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-blue-600" />
                  <span>Scene Duration:</span>
                </span>
                <select
                  value={targetDuration}
                  onChange={(e) => setTargetDuration(Number(e.target.value))}
                  className="bg-transparent text-xs font-extrabold text-blue-700 focus:outline-none cursor-pointer"
                >
                  <option value={6}>6s / scene</option>
                  <option value={7}>7s / scene</option>
                  <option value={8}>8s / scene (Standard)</option>
                  <option value={9}>9s / scene</option>
                  <option value={10}>10s / scene</option>
                  <option value={12}>12s / scene</option>
                </select>
                <span className="text-[11px] text-[#86868B] font-semibold pl-1">
                  (→ {plannedScenesCount} scenes)
                </span>
              </div>
            </div>

            {/* Hidden audio element */}
            <audio
              ref={audioPlayerRef}
              src={`/api/v1/projects/${selectedProjectId}/audio-flow/stream?t=${Date.now()}`}
              onEnded={() => setIsPlayingAudio(false)}
            />

            {/* Lyric Snippets Preview */}
            {audioTimeline.lyric_timestamps && audioTimeline.lyric_timestamps.length > 0 && (
              <div className="bg-white border border-[#E5E5EA] rounded-xl p-3 max-h-32 overflow-y-auto space-y-1">
                <p className="text-[10px] font-bold uppercase tracking-wider text-[#86868B] pb-1">
                  Synchronized SRT Lyrics:
                </p>
                {audioTimeline.lyric_timestamps.slice(0, 8).map((l, i) => (
                  <div key={i} className="text-xs text-[#1D1D1F] flex items-center justify-between">
                    <span className="font-mono text-[10px] text-[#86868B]">
                      {l.start?.toFixed(1)}s – {l.end?.toFixed(1)}s
                    </span>
                    <span className="font-medium truncate max-w-md">{l.line}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="bg-[#FAFAFC] border border-dashed border-[#E5E5EA] rounded-2xl p-8 text-center space-y-2">
            <Music className="w-8 h-8 text-amber-500 mx-auto opacity-70" />
            <p className="text-xs text-[#86868B]">
              No song audio found for this project. Generate audio or upload an MP3/WAV file.
            </p>
          </div>
        )}
      </section>

      {/* ─────────────────────────────────────────────────────────────────── */}
      {/* STEP 5: SCENE PLANNING                                              */}
      {/* ─────────────────────────────────────────────────────────────────── */}
      <section className="bg-white border border-[#E5E5EA] rounded-3xl p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E5E5EA] pb-4">
          <div className="space-y-0.5">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-purple-50 text-purple-800 border border-purple-200">
              <Clapperboard className="w-3.5 h-3.5 text-purple-600" />
              <span>Step 5 • Scene Planning</span>
            </div>
            <h3 className="text-lg font-bold text-[#1D1D1F]">Generate Storyboard Scenes</h3>
            <p className="text-xs text-[#6E6E73]">
              Plans exact {targetDuration}s scenes mapped from song duration ({songDuration.toFixed(1)}s ÷ {targetDuration}s = {plannedScenesCount} scenes).
            </p>
          </div>

          <button
            onClick={handlePlanScenes}
            disabled={planningScenes || !selectedProjectId}
            className="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-2xl text-xs font-bold transition-all shadow-md shadow-purple-500/20 flex items-center gap-2"
          >
            {planningScenes ? <Loader2 className="w-4 h-4 animate-spin" /> : <Clapperboard className="w-4 h-4" />}
            <span>{planningScenes ? "Planning Scenes…" : `🎬 Plan Storyboard Scenes (${targetDuration}s each)`}</span>
          </button>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────────── */}
      {/* STEP 6-9: SCENE PROMPTS & COPY TRACKING (GREEN INDICATOR & COUNTER) */}
      {/* ─────────────────────────────────────────────────────────────────── */}
      <section className="bg-white border border-[#E5E5EA] rounded-3xl p-6 shadow-xs space-y-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#E5E5EA] pb-4">
          <div className="space-y-0.5">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Step 6 to 9 • Scene Prompts & Copy Tracking</span>
            </div>
            <h3 className="text-lg font-bold text-[#1D1D1F]">Ready-to-Copy Scene Prompts</h3>
            <p className="text-xs text-[#6E6E73]">
              Copy each scene prompt with 1-click. Green indicator marks copied prompts for external generation in Google Flow.
            </p>
          </div>

          {/* Copy all button */}
          {scenes.length > 0 && (
            <button
              onClick={() => {
                const fullText = scenes
                  .map(
                    (s) =>
                      `=== SCENE ${String(s.scene_number).padStart(2, "0")} (${s.duration?.toFixed(1)}s) ===\n${
                        s.video_prompt || s.dialogue || s.lyrics || ""
                      }`
                  )
                  .join("\n\n");
                copyToClipboard(fullText, "all_scenes");
              }}
              className="flex items-center gap-1.5 px-4 py-2 bg-[#FAFAFC] hover:bg-[#F5F5F7] border border-[#E5E5EA] rounded-2xl text-xs font-bold text-[#1D1D1F] transition-all"
            >
              {copiedKey === "all_scenes" ? <Check className="w-3.5 h-3.5 text-green-600" /> : <Copy className="w-3.5 h-3.5 text-[#86868B]" />}
              <span>{copiedKey === "all_scenes" ? "ALL COPIED ✓" : "Copy All Prompts"}</span>
            </button>
          )}
        </div>

        {/* Step 11: Scene Counter at top */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-[#FAFAFC] border border-[#E5E5EA] rounded-2xl p-4">
          <div className="text-center">
            <p className="text-2xl font-black text-[#1D1D1F]">{totalScenes}</p>
            <p className="text-[10px] font-extrabold uppercase tracking-wider text-[#86868B]">Total Planned Scenes</p>
          </div>
          <div className="text-center border-l sm:border-r border-[#E5E5EA]">
            <p className={`text-2xl font-black ${allCopied ? "text-emerald-600" : "text-[#1D1D1F]"}`}>
              {copiedCount} / {totalScenes}
            </p>
            <p className="text-[10px] font-extrabold uppercase tracking-wider text-[#86868B] flex items-center justify-center gap-1">
              {allCopied && <CheckCircle2 className="w-3 h-3 text-emerald-600" />}
              <span>Prompt Copied</span>
            </p>
          </div>
          <div className="text-center">
            <p className={`text-2xl font-black ${allUploaded ? "text-purple-600" : "text-[#1D1D1F]"}`}>
              {uploadedCount} / {totalScenes}
            </p>
            <p className="text-[10px] font-extrabold uppercase tracking-wider text-[#86868B]">Videos Uploaded</p>
          </div>
        </div>

        {/* Workflow Tip Banner */}
        <div className="bg-blue-50/70 border border-blue-200/80 rounded-2xl p-4 flex items-start gap-3">
          <ExternalLink className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="text-xs text-blue-900 leading-relaxed">
            <strong>External AI Generation Workflow:</strong> Click <strong>COPY SCENE</strong> below → Paste into{" "}
            <a
              href="https://labs.google/flow/"
              target="_blank"
              rel="noopener noreferrer"
              className="underline font-bold hover:text-blue-700"
            >
              Google Flow
            </a>{" "}
            or your preferred AI video generator → Download the video → Upload it below in Step 10.
          </div>
        </div>

        {/* Scenes List */}
        {scenes.length === 0 ? (
          <div className="bg-[#FAFAFC] border border-dashed border-[#E5E5EA] rounded-2xl p-8 text-center space-y-3">
            <Clapperboard className="w-8 h-8 text-[#FF6B00] mx-auto opacity-70" />
            <p className="text-xs text-[#86868B]">No scenes planned yet. Click "Plan Storyboard Scenes" above.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {scenes.map((scene) => {
              const isCopied = scene.prompt_status && scene.prompt_status !== "NOT_COPIED";
              const isUploaded = scene.prompt_status === "VIDEO_UPLOADED" || scene.prompt_status === "ORDER_CONFIRMED";
              const isJustCopied = justCopiedSceneId === scene.id;
              const isExpanded = expandedSceneId === scene.id;
              const promptText = scene.video_prompt || scene.dialogue || `Scene ${scene.scene_number}: ${scene.lyrics || ""}`;

              return (
                <div
                  key={scene.id}
                  className={`border rounded-2xl transition-all ${
                    isUploaded
                      ? "border-purple-200 bg-purple-50/20"
                      : isCopied
                      ? "border-emerald-200 bg-emerald-50/30"
                      : "border-[#E5E5EA] bg-white"
                  }`}
                >
                  <div className="flex items-center justify-between p-4 gap-3">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      {/* Step 10: Visual green dot / indicator */}
                      <div
                        className={`w-3 h-3 rounded-full flex-shrink-0 ${
                          isUploaded
                            ? "bg-purple-600 ring-4 ring-purple-100"
                            : isCopied
                            ? "bg-emerald-500 ring-4 ring-emerald-100"
                            : "bg-[#C7C7CC]"
                        }`}
                        title={isUploaded ? "Video Uploaded" : isCopied ? "Prompt Copied" : "Not Copied"}
                      />
                      <span className="font-bold text-[#1D1D1F] text-sm">
                        Scene {String(scene.scene_number).padStart(2, "0")}
                      </span>
                      <span className="text-[#86868B] text-xs flex items-center gap-1 font-mono">
                        <Clock className="w-3 h-3" />
                        {scene.start_time?.toFixed(1)}s – {scene.end_time?.toFixed(1)}s ({scene.duration?.toFixed(1)}s)
                      </span>
                      {scene.lyrics && (
                        <span className="text-[#1D1D1F] text-xs italic truncate max-w-sm hidden sm:inline">
                          "{scene.lyrics}"
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-2 flex-shrink-0">
                      {/* Badges */}
                      {isUploaded && (
                        <span className="text-[11px] font-bold text-purple-700 bg-purple-100 px-2.5 py-0.5 rounded-full">
                          ✓ Video Uploaded
                        </span>
                      )}
                      {isCopied && !isUploaded && (
                        <span className="text-[11px] font-bold text-emerald-700 bg-emerald-100 px-2.5 py-0.5 rounded-full">
                          ● Prompt Copied
                        </span>
                      )}
                      {!isCopied && (
                        <span className="text-[11px] font-semibold text-[#86868B] bg-[#F5F5F7] px-2.5 py-0.5 rounded-full">
                          ○ Not Copied
                        </span>
                      )}

                      <button
                        onClick={() => setExpandedSceneId(isExpanded ? null : scene.id)}
                        className="p-1.5 rounded-xl hover:bg-[#F5F5F7] text-[#86868B] transition-colors"
                        title="View prompt details"
                      >
                        <ChevronDown className={`w-4 h-4 transition-transform ${isExpanded ? "rotate-180" : ""}`} />
                      </button>

                      {/* Single Click Copy Scene Button */}
                      <button
                        onClick={() => handleCopyScenePrompt(scene)}
                        className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all shadow-xs ${
                          isJustCopied
                            ? "bg-emerald-600 text-white"
                            : isCopied
                            ? "bg-emerald-100 text-emerald-800 hover:bg-emerald-200"
                            : "bg-[#FF6B00] hover:bg-[#EA580C] text-white"
                        }`}
                      >
                        {isJustCopied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                        <span>{isJustCopied ? "COPIED ✓" : isCopied ? "Copy Again" : "COPY SCENE"}</span>
                      </button>
                    </div>
                  </div>

                  {/* Expanded Prompt Details */}
                  {isExpanded && (
                    <div className="px-4 pb-4 border-t border-[#F5F5F7] space-y-3 pt-3">
                      <div className="bg-[#1D1D1F] rounded-xl p-3.5">
                        <p className="text-[#F5F5F7] text-xs font-mono leading-relaxed whitespace-pre-wrap select-all">
                          {promptText}
                        </p>
                      </div>
                      <div className="flex flex-wrap items-center justify-between text-[11px] text-[#86868B] gap-2">
                        <span>Target Duration: <strong>{scene.duration?.toFixed(1)}s</strong></span>
                        {scene.camera_prompt && <span>Camera: {scene.camera_prompt}</span>}
                        {scene.uploaded_file && (
                          <span className="text-purple-700 font-semibold">
                            Uploaded: {scene.uploaded_file.split("/").pop()} ({scene.uploaded_duration?.toFixed(1)}s)
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* ─────────────────────────────────────────────────────────────────── */}
      {/* STEP 10-12: SCENE VIDEO UPLOAD & DETERMINISTIC IDENTIFICATION        */}
      {/* ─────────────────────────────────────────────────────────────────── */}
      <section className="bg-white border border-[#E5E5EA] rounded-3xl p-6 shadow-xs space-y-5">
        <div className="border-b border-[#E5E5EA] pb-4">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-indigo-50 text-indigo-800 border border-indigo-200 mb-1">
            <UploadCloud className="w-3.5 h-3.5 text-indigo-600" />
            <span>Step 10 to 12 • Scene Video Upload</span>
          </div>
          <h3 className="text-lg font-bold text-[#1D1D1F]">Upload Generated Scene Videos</h3>
          <p className="text-xs text-[#6E6E73]">
            Drag & drop your AI-generated videos (MP4, MOV, WEBM). Files named <code>scene_01.mp4</code> or <code>01.mp4</code> auto-map to Scene 1.
          </p>
        </div>

        {/* Drag & Drop Zone */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            handleBatchUpload(e.dataTransfer.files);
          }}
          className={`border-2 border-dashed rounded-3xl p-8 text-center transition-all ${
            dragOver ? "border-[#FF6B00] bg-orange-50/50" : "border-[#E5E5EA] bg-[#FAFAFC] hover:border-[#FF6B00]/60"
          }`}
        >
          <input
            type="file"
            ref={videoFileInputRef}
            onChange={(e) => handleBatchUpload(e.target.files)}
            multiple
            accept="video/mp4,video/quicktime,video/webm"
            className="hidden"
          />

          <div className="space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 border border-indigo-100 flex items-center justify-center mx-auto shadow-xs">
              {uploadingVideos ? <Loader2 className="w-6 h-6 animate-spin text-[#FF6B00]" /> : <UploadCloud className="w-6 h-6" />}
            </div>
            <div>
              <p className="text-sm font-bold text-[#1D1D1F]">
                {uploadingVideos ? "Uploading & Validating Video Durations…" : "Drag & Drop Scene Videos Here"}
              </p>
              <p className="text-xs text-[#86868B] mt-1">Supports MP4, MOV, WEBM • Multiple files accepted</p>
            </div>
            <button
              onClick={() => videoFileInputRef.current?.click()}
              disabled={uploadingVideos || !selectedProjectId}
              className="px-5 py-2.5 bg-[#FF6B00] hover:bg-[#EA580C] text-white rounded-2xl text-xs font-bold transition-all shadow-md shadow-orange-500/20"
            >
              Browse Video Files
            </button>
          </div>
        </div>

        {/* Unresolved Files Manual Assignment Dropdown (Section 18) */}
        {unresolved.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 space-y-3">
            <div className="flex items-center gap-2 text-amber-900 font-bold text-xs">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <span>Unresolved Video Filenames — Manual Assignment Required:</span>
            </div>
            <div className="space-y-2">
              {unresolved.map((u, i) => (
                <div key={i} className="flex items-center justify-between bg-white border border-amber-200 rounded-xl p-3 text-xs">
                  <span className="font-mono text-[#1D1D1F] font-semibold">{u.filename}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[#86868B]">Assign to:</span>
                    <select
                      value={assigningFile?.tmp_path === u.tmp_path ? assignTargetScene : 1}
                      onChange={(e) => {
                        setAssigningFile(u);
                        setAssignTargetScene(Number(e.target.value));
                      }}
                      className="border border-[#E5E5EA] rounded-lg px-2 py-1 font-bold text-xs"
                    >
                      {scenes.map((s) => (
                        <option key={s.scene_number} value={s.scene_number}>
                          Scene {String(s.scene_number).padStart(2, "0")}
                        </option>
                      ))}
                    </select>
                    <button
                      onClick={() => {
                        setAssigningFile(u);
                        handleAssignUnresolved();
                      }}
                      className="px-3 py-1 bg-amber-600 text-white rounded-lg font-bold text-xs hover:bg-amber-700"
                    >
                      Assign
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* ─────────────────────────────────────────────────────────────────── */}
      {/* STEP 13-14: ORDERED SCENE VIEW & SEQUENCE CONFIRMATION              */}
      {/* ─────────────────────────────────────────────────────────────────── */}
      <section className="bg-white border border-[#E5E5EA] rounded-3xl p-6 shadow-xs space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E5E5EA] pb-4">
          <div className="space-y-0.5">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-cyan-50 text-cyan-800 border border-cyan-200">
              <ListOrdered className="w-3.5 h-3.5 text-cyan-600" />
              <span>Step 13 & 14 • Sequence Verification</span>
            </div>
            <h3 className="text-lg font-bold text-[#1D1D1F]">Final Scene Sequence</h3>
            <p className="text-xs text-[#6E6E73]">
              Confirm that all scene videos are mapped in correct chronological order before assembly.
            </p>
          </div>

          <button
            onClick={handleConfirmSequence}
            disabled={confirmingSequence || scenes.length === 0}
            className={`px-5 py-2.5 rounded-2xl text-xs font-bold transition-all shadow-md flex items-center gap-2 ${
              sequenceConfirmed
                ? "bg-emerald-600 text-white shadow-emerald-500/20"
                : "bg-cyan-600 hover:bg-cyan-700 text-white shadow-cyan-500/20"
            }`}
          >
            {confirmingSequence ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : sequenceConfirmed ? (
              <CheckCircle2 className="w-4 h-4" />
            ) : (
              <Check className="w-4 h-4" />
            )}
            <span>{sequenceConfirmed ? "Sequence Confirmed ✓" : "Confirm Scene Sequence"}</span>
          </button>
        </div>

        {/* Sequence Badges */}
        <div className="flex flex-wrap items-center gap-2 p-3 bg-[#FAFAFC] border border-[#E5E5EA] rounded-2xl">
          {scenes.map((s, idx) => {
            const hasVideo = !!s.uploaded_file;
            return (
              <div key={s.id} className="flex items-center gap-1.5">
                <span
                  className={`px-2.5 py-1 rounded-xl text-xs font-bold flex items-center gap-1 ${
                    hasVideo ? "bg-emerald-100 text-emerald-800" : "bg-red-50 text-red-700 border border-red-200"
                  }`}
                >
                  <span>{String(s.scene_number).padStart(2, "0")}</span>
                  {hasVideo ? <Check className="w-3 h-3 text-emerald-600" /> : <X className="w-3 h-3 text-red-500" />}
                </span>
                {idx < scenes.length - 1 && <span className="text-[#C7C7CC] text-xs">→</span>}
              </div>
            );
          })}
        </div>

        {/* Missing Scenes Alert (Section 23) */}
        {!allUploaded && totalScenes > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 text-xs text-amber-900 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
            <span>
              <strong>{totalScenes - uploadedCount} scenes are still missing videos:</strong>{" "}
              {scenes
                .filter((s) => !s.uploaded_file)
                .map((s) => `Scene ${String(s.scene_number).padStart(2, "0")}`)
                .join(", ")}
              . Upload them above before final assembly.
            </span>
          </div>
        )}
      </section>

      {/* ─────────────────────────────────────────────────────────────────── */}
      {/* STEP 15-16: FINAL VIDEO ASSEMBLY WITH FFMPEG & PREVIEW PLAYER       */}
      {/* ─────────────────────────────────────────────────────────────────── */}
      <section className="bg-white border border-[#E5E5EA] rounded-3xl p-6 shadow-xs space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E5E5EA] pb-4">
          <div className="space-y-0.5">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-green-50 text-green-800 border border-green-200">
              <Film className="w-3.5 h-3.5 text-green-600" />
              <span>Step 15 & 16 • Final Assembly</span>
            </div>
            <h3 className="text-lg font-bold text-[#1D1D1F]">FFmpeg Automatic Video Assembly</h3>
            <p className="text-xs text-[#6E6E73]">
              Combines ordered scene videos + master song audio + SRT subtitles into the complete final YouTube MP4.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCheckReadiness}
              disabled={checkingReadiness || !selectedProjectId}
              className="px-3.5 py-2 border border-[#E5E5EA] bg-[#FAFAFC] hover:bg-[#F5F5F7] rounded-xl text-xs font-bold text-[#1D1D1F] transition-all"
            >
              {checkingReadiness ? "Checking…" : "Check Readiness"}
            </button>
            <button
              onClick={handleGenerateFinalVideo}
              disabled={assembling || !selectedProjectId || !allUploaded}
              className="px-6 py-2.5 bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white rounded-2xl text-xs font-black transition-all shadow-lg shadow-emerald-500/25 flex items-center gap-2 disabled:opacity-50"
            >
              {assembling ? <Loader2 className="w-4 h-4 animate-spin" /> : <Film className="w-4 h-4" />}
              <span>{assembling ? "Assembling Final Video with FFmpeg…" : "🚀 GENERATE FINAL VIDEO"}</span>
            </button>
          </div>
        </div>

        {/* Readiness Info */}
        {readiness && (
          <div className="p-4 bg-[#FAFAFC] border border-[#E5E5EA] rounded-2xl text-xs space-y-1">
            <p className="font-bold text-[#1D1D1F]">Assembly Pre-Flight Status:</p>
            <div className="flex flex-wrap gap-4 text-[#6E6E73] pt-1">
              <span>All Videos Uploaded: {readiness.uploaded_scenes}/{readiness.total_scenes} {readiness.missing_scenes.length === 0 ? "✓" : "✗"}</span>
              <span>Audio Track: {readiness.audio_available ? "✓ Available" : "✗ Missing"}</span>
              <span>SRT Lyrics: {readiness.srt_available ? "✓ Available" : "✗ Missing"}</span>
            </div>
          </div>
        )}

        {/* Assemble Error Banner */}
        {assembleError && (
          <div className="bg-red-50 border border-red-200 rounded-2xl p-4 text-xs text-red-800">
            <strong>Error:</strong> {assembleError}
          </div>
        )}

        {/* Final Video Result Player */}
        {finalVideoResult && (
          <div className="bg-[#FAFAFC] border border-emerald-300 rounded-3xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-800 font-bold text-sm">
                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                <span>Final Video Assembled Successfully! ({finalVideoResult.duration?.toFixed(1)}s)</span>
              </div>
              <a
                href={`/api/v1/projects/${selectedProjectId}/assembly/final-video`}
                download={`${activeProject?.title || "kids_song"}.mp4`}
                className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-emerald-500/20"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download MP4</span>
              </a>
            </div>

            <div className="rounded-2xl overflow-hidden bg-black aspect-video max-w-3xl mx-auto shadow-xl">
              <video
                src={`/api/v1/projects/${selectedProjectId}/assembly/final-video?t=${Date.now()}`}
                controls
                className="w-full h-full"
              />
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
