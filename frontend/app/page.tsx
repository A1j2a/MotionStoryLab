"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import Link from "next/link";
import { Header } from "@/components/Header";
import { TopicDiscovery } from "@/components/TopicDiscovery";
import { ContentPackageEditor } from "@/components/ContentPackageEditor";
import { StoryboardView } from "@/components/StoryboardView";
import { QCCheckView } from "@/components/QCCheckView";
import { ManualWorkflowView } from "@/components/ManualWorkflowView";
import { api } from "@/lib/api";
import {
  Project,
  DashboardStats,
  TopicOpportunity,
  ContentPackage,
  Scene,
  AudioTimeline,
  QCResult,
  SunoPromptPackage,
} from "@/lib/types";
import {
  Film,
  Sparkles,
  Clapperboard,
  HardDrive,
  ArrowRight,
  PlusCircle,
  Play,
  Pause,
  Clock,
  CheckCircle2,
  Terminal,
  RotateCcw,
  Music,
  ShieldCheck,
  FileVideo,
  Loader2,
  Radio,
  ExternalLink,
  Check,
  Copy,
  UploadCloud,
  Download,
  ChevronRight,
  Flame,
  Power,
  PowerOff,
  Trash2,
  Zap,
  Lock,
} from "lucide-react";

const ACTIVE_PROJ_KEY = "motionstory_active_project_id";
const WORKFLOW_ACTIVE_KEY = "motionstory_workflow_active";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  // Workflow Master Switch (ON / OFF)
  const [workflowActive, setWorkflowActive] = useState<boolean>(true);
  const [workflowMode, setWorkflowMode] = useState<"manual" | "legacy">("manual");

  // Active workflow state
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [contentPkg, setContentPkg] = useState<ContentPackage | null>(null);
  const [audioTimeline, setAudioTimeline] = useState<AudioTimeline | null>(null);
  const [sunoPackage, setSunoPackage] = useState<SunoPromptPackage | null>(null);
  const [uploadingAudio, setUploadingAudio] = useState(false);
  const [copiedSuno, setCopiedSuno] = useState<string | null>(null);
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [qcResult, setQcResult] = useState<QCResult | null>(null);
  const [targetSceneDuration, setTargetSceneDuration] = useState<number>(8);

  // Workflow progress actions
  const [songLoading, setSongLoading] = useState(false);
  const [renderLoading, setRenderLoading] = useState(false);
  const [qcLoading, setQcLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  // Audio player state
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [audioCacheBust, setAudioCacheBust] = useState(Date.now());
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const pollTimerRef = useRef<NodeJS.Timeout | null>(null);

  const loadDashboardData = async () => {
    try {
      const [statsData, projectsData] = await Promise.all([
        api.getDashboardStats().catch(() => null),
        api.getProjects().catch(() => []),
      ]);
      if (statsData) setStats(statsData);
      if (projectsData) setProjects(projectsData);
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  const restoreActiveProjectState = useCallback(async (projectId: string) => {
    try {
      const proj = await api.getProject(projectId);
      if (!proj) return;
      setActiveProject(proj);

      // Restore downstream stages in parallel
      const [pkg, timeline, qc] = await Promise.all([
        api.getContentPackage(projectId).catch(() => null),
        api.getAudioTimeline(projectId).catch(() => null),
        api.getQCReport(projectId).catch(() => null),
      ]);

      if (pkg) setContentPkg(pkg);
      if (timeline) setAudioTimeline(timeline);
      if (qc) setQcResult(qc);
      if (proj.scenes && proj.scenes.length > 0) setScenes(proj.scenes);
    } catch {
      localStorage.removeItem(ACTIVE_PROJ_KEY);
    }
  }, []);

  // Initial load & Restore persistence from localStorage
  useEffect(() => {
    loadDashboardData();

    const savedWorkflow = localStorage.getItem(WORKFLOW_ACTIVE_KEY);
    if (savedWorkflow !== null) {
      setWorkflowActive(savedWorkflow === "true");
    }

    const savedProjectId = localStorage.getItem(ACTIVE_PROJ_KEY);
    if (savedProjectId) {
      restoreActiveProjectState(savedProjectId);
    }
  }, [restoreActiveProjectState]);

  // Synchronize active project ID with localStorage
  useEffect(() => {
    if (activeProject) {
      localStorage.setItem(ACTIVE_PROJ_KEY, activeProject.id);
    }
  }, [activeProject]);

  // Controlled, safe polling (only when workflow is ON and project is in active processing)
  useEffect(() => {
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }

    if (!workflowActive || !activeProject) return;

    const isProcessing =
      activeProject.status === "PROCESSING" ||
      (activeProject.jobs &&
        activeProject.jobs.length > 0 &&
        ["PLANNING", "AUDIO_GENERATION", "RENDERING", "COMPOSITING", "SCENE_RENDERING"].includes(
          activeProject.jobs[0].status
        ));

    if (!isProcessing) return;

    pollTimerRef.current = setInterval(async () => {
      try {
        const p = await api.getProject(activeProject.id);
        if (p) {
          setActiveProject(p);
          if (p.scenes) setScenes(p.scenes);
        }
      } catch {
        // ignore intermittent errors
      }
    }, 3000);

    return () => {
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
        pollTimerRef.current = null;
      }
    };
  }, [workflowActive, activeProject?.id, activeProject?.status]);

  // Toggle Workflow Master Switch
  const handleToggleWorkflow = () => {
    const nextState = !workflowActive;
    setWorkflowActive(nextState);
    localStorage.setItem(WORKFLOW_ACTIVE_KEY, String(nextState));
  };

  // Reset / Clear Active Production
  const handleResetActiveProject = () => {
    if (!confirm("Are you sure you want to clear current active production from the studio workspace? Progress will remain saved in database.")) {
      return;
    }
    localStorage.removeItem(ACTIVE_PROJ_KEY);
    setActiveProject(null);
    setContentPkg(null);
    setAudioTimeline(null);
    setScenes([]);
    setQcResult(null);
    setUploadSuccess(null);
  };

  // Step 1: Handle selecting topic
  const handleSelectTopic = async (topic: TopicOpportunity) => {
    try {
      const project = await api.selectTopic({
        topic: topic.topic,
        title: topic.suggested_title,
        category: topic.category,
        target_age: topic.target_age,
        duration: topic.duration || "2–3 Minutes",
        content_angle: topic.content_angle,
        why_worth_considering: topic.why_worth_considering,
        opportunity_signals: topic.opportunity_signals,
        suggested_characters: topic.suggested_characters,
        suggested_story_concept: topic.suggested_story_concept,
      });

      setActiveProject(project);

      // Auto-fetch/generate content package
      const pkg = await api.generateContentPackage(project.id);
      setContentPkg(pkg);

      // Refresh project list in background
      loadDashboardData();
    } catch (err: any) {
      alert("Failed to initialize project from topic: " + err.message);
    }
  };

  // Fetch Suno AI Prompt Package
  const handleLoadSunoPrompt = async () => {
    if (!activeProject) return;
    try {
      const pkg = await api.getSunoPrompt(activeProject.id);
      setSunoPackage(pkg);
    } catch (err: any) {
      console.error("Failed to load Suno prompt:", err);
    }
  };

  // Upload Suno AI Song Track with synchronized Musical Section Map & Video Prompts
  const handleAudioUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !activeProject) return;
    setUploadingAudio(true);
    try {
      const res = await api.uploadSongAudio(activeProject.id, file, contentPkg?.approved_lyrics);
      if (res && res.timeline) {
        setAudioTimeline(res.timeline);

        // Refresh project and storyboard scenes with dedicated 3D video prompts
        const [updatedProject, sbScenes] = await Promise.all([
          api.getProject(activeProject.id).catch(() => null),
          api.getScenes(activeProject.id).catch(() => []),
        ]);
        if (updatedProject) setActiveProject(updatedProject);
        if (sbScenes && sbScenes.length > 0) setScenes(sbScenes);

        // Force reload audio player with uploaded song
        setAudioCacheBust(Date.now());
        if (audioRef.current) {
          audioRef.current.src = `${api.getSongAudioUrl(activeProject.id)}?t=${Date.now()}`;
          audioRef.current.load();
          setIsPlayingAudio(false);
        }

        alert("Song uploaded and timeline synchronized successfully!\n• Subtitles (.srt) regenerated\n• Musical Section Map updated with uploaded audio\n• 3D Video Generation Prompts ready with copy button for every scene!");
      }
    } catch (err: any) {
      alert("Audio upload failed: " + err.message);
    } finally {
      setUploadingAudio(false);
    }
  };

  const copySunoText = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedSuno(key);
    setTimeout(() => setCopiedSuno(null), 2000);
  };

  // Step 3: Trigger Song Generation from exact approved lyrics
  const handleGenerateSong = async () => {
    if (!activeProject) return;
    setSongLoading(true);
    try {
      await api.generateSong(activeProject.id);
      let attempts = 0;
      const poll = setInterval(async () => {
        attempts++;
        try {
          const timeline = await api.getAudioTimeline(activeProject.id);
          if (timeline && timeline.sections && timeline.sections.length > 0) {
            setAudioTimeline(timeline);
            clearInterval(poll);
            setSongLoading(false);

            // Auto generate storyboard scenes
            const sbScenes = await api.generateStoryboard(activeProject.id, targetSceneDuration);
            setScenes(sbScenes);
          }
        } catch {
          // keep polling
        }
        if (attempts > 20) {
          clearInterval(poll);
          setSongLoading(false);
        }
      }, 2500);
    } catch (err: any) {
      alert("Song generation failed: " + err.message);
      setSongLoading(false);
    }
  };

  // Step 5 & 6: Render 3D Scenes with Real-Time Progress Polling
  const handleRenderScenes = async () => {
    if (!activeProject) return;
    setRenderLoading(true);
    try {
      await api.renderScenes(activeProject.id);
      
      let attempts = 0;
      const poll = setInterval(async () => {
        attempts++;
        try {
          const p = await api.getProject(activeProject.id);
          if (p) {
            setActiveProject(p);
            if (p.scenes) setScenes(p.scenes);
            const allDone = p.scenes && p.scenes.length > 0 && p.scenes.every((s: any) => s.status === "COMPLETED");
            if (allDone || p.status === "READY" || p.status === "READY_FOR_REVIEW") {
              clearInterval(poll);
              setRenderLoading(false);
              loadDashboardData();
            }
          }
        } catch {
          // ignore transient poll error
        }
        if (attempts > 120) { // 5 minutes max timeout
          clearInterval(poll);
          setRenderLoading(false);
        }
      }, 2500);
    } catch (err: any) {
      alert("Scene rendering failed: " + err.message);
      setRenderLoading(false);
    }
  };

  // Step 8: Quality Control Check
  const handleRunQC = async () => {
    if (!activeProject) return;
    setQcLoading(true);
    try {
      const res = await api.runQC(activeProject.id);
      setQcResult(res);
    } catch (err: any) {
      alert("QC check failed: " + err.message);
    } finally {
      setQcLoading(false);
    }
  };

  // Step 10: Private YouTube Upload
  const handleYouTubeUpload = async () => {
    if (!activeProject) return;
    setUploadLoading(true);
    setUploadSuccess(null);
    try {
      const res = await api.uploadYouTube(activeProject.id, "private");
      setUploadSuccess(res.message || "Video uploaded strictly in PRIVATE mode.");
    } catch (err: any) {
      alert("YouTube upload failed: " + err.message);
    } finally {
      setUploadLoading(false);
    }
  };

  const toggleAudioPlayback = () => {
    if (!audioRef.current) return;
    if (isPlayingAudio) {
      audioRef.current.pause();
      setIsPlayingAudio(false);
    } else {
      audioRef.current.play();
      setIsPlayingAudio(true);
    }
  };

  return (
    <>
      <Header
        title="AI Kids Video Production Studio"
        subtitle="10-Step Automated 3D Kids & Nursery Rhyme Production Workflow"
      />

      <main className="p-8 space-y-8 flex-1 max-w-6xl mx-auto w-full">
        {/* Studio Status & Master Process Control Bar */}
        <div className="bg-white border border-[#E5E5EA] rounded-2xl p-4 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center border ${
              workflowActive ? "bg-emerald-50 text-emerald-600 border-emerald-200" : "bg-slate-100 text-slate-500 border-slate-200"
            }`}>
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm text-[#1D1D1F]">Pipeline Master Control</span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  workflowActive ? "bg-emerald-100 text-emerald-800" : "bg-slate-100 text-slate-700"
                }`}>
                  {workflowActive ? "PROCESS RUNNING (ON)" : "PROCESS PAUSED (OFF)"}
                </span>
              </div>
              <p className="text-xs text-[#86868B] mt-0.5">
                {activeProject
                  ? `Active Production: "${activeProject.title}" • Status: ${activeProject.status}`
                  : "No active production selected. Discover or pick a topic below."}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            {/* Master Process Switch Button */}
            <button
              onClick={handleToggleWorkflow}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 shadow-xs ${
                workflowActive
                  ? "bg-[#10B981] hover:bg-[#059669] text-white"
                  : "bg-slate-700 hover:bg-slate-800 text-white"
              }`}
            >
              <Power className="w-3.5 h-3.5" />
              <span>{workflowActive ? "Process: ON" : "Process: OFF"}</span>
            </button>

            {/* Clear / Start Fresh Button */}
            {activeProject && (
              <button
                onClick={handleResetActiveProject}
                className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-[#FEF2F2] text-[#DC2626] hover:bg-[#FEE2E2] border border-[#FECACA] transition-all cursor-pointer flex items-center gap-1.5"
                title="Reset workspace to select a new topic"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Reset / New Topic</span>
              </button>
            )}
          </div>
        </div>

        {/* Studio Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-5 shadow-xs space-y-2">
            <div className="flex items-center justify-between text-[#6E6E73]">
              <span className="text-xs font-bold uppercase tracking-wider">Total Productions</span>
              <Film className="w-4 h-4 text-[#FF6B00]" />
            </div>
            <div className="text-2xl font-extrabold text-[#1D1D1F]">
              {stats?.total_projects || projects.length}
            </div>
            <p className="text-[11px] text-[#86868B]">In local SQLite studio DB</p>
          </div>

          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-5 shadow-xs space-y-2">
            <div className="flex items-center justify-between text-[#6E6E73]">
              <span className="text-xs font-bold uppercase tracking-wider">Active Jobs</span>
              <Sparkles className="w-4 h-4 text-[#FF6B00]" />
            </div>
            <div className="text-2xl font-extrabold text-[#1D1D1F]">
              {stats?.active_jobs || 0}
            </div>
            <p className="text-[11px] text-[#86868B]">Sequential M4 background jobs</p>
          </div>

          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-5 shadow-xs space-y-2">
            <div className="flex items-center justify-between text-[#6E6E73]">
              <span className="text-xs font-bold uppercase tracking-wider">3D Scenes Rendered</span>
              <Clapperboard className="w-4 h-4 text-[#FF6B00]" />
            </div>
            <div className="text-2xl font-extrabold text-[#1D1D1F]">
              {stats?.completed_scenes || scenes.filter((s) => s.status === "COMPLETED").length}
            </div>
            <p className="text-[11px] text-emerald-600 font-semibold">100% locally on Storybook 3D Engine (FFmpeg)</p>
          </div>

          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-5 shadow-xs space-y-2">
            <div className="flex items-center justify-between text-[#6E6E73]">
              <span className="text-xs font-bold uppercase tracking-wider">Disk Storage</span>
              <HardDrive className="w-4 h-4 text-[#FF6B00]" />
            </div>
            <div className="text-2xl font-extrabold text-[#1D1D1F]">
              {stats ? `${stats.storage_used_mb} MB` : "14.2 MB"}
            </div>
            <p className="text-[11px] text-[#86868B]">Local /projects media storage</p>
          </div>
        </div>

        {/* STEP 1: DISCOVER TOPICS */}
        <section className="space-y-4">
          <TopicDiscovery onSelectTopic={handleSelectTopic} />
        </section>

        {/* STEP 2 & 4: CONTENT PACKAGE & APPROVED LYRICS (SOURCE OF TRUTH) */}
        {activeProject && contentPkg && (
          <section className="space-y-4">
            <ContentPackageEditor
              projectId={activeProject.id}
              initialPackage={contentPkg}
              onSaved={(saved) => setContentPkg(saved)}
            />
          </section>
        )}

        {/* STEP 3 & 7: GENERATE SONG FROM EXACT APPROVED LYRICS */}
        {activeProject && (
          <section className="bg-white border border-[#E5E5EA] rounded-3xl p-6 shadow-xs space-y-5">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#E5E5EA]">
              <div className="space-y-1">
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-800 border border-amber-200">
                  <Music className="w-3.5 h-3.5 text-amber-600" />
                  <span>Step 3 • Song Generation & Suno AI Hub</span>
                </div>
                <h2 className="text-lg font-bold text-[#1D1D1F]">
                  Master Nursery Song & Audio Timeline Synchronization
                </h2>
                <p className="text-xs text-[#6E6E73]">
                  Generate automatically with local neural voices or use Suno AI with custom prompt & drag-and-drop audio upload.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-2.5">
                {/* Per-Scene Target Duration Selector */}
                <div className="flex items-center gap-1.5 bg-[#FAFAFC] border border-[#E5E5EA] px-3 py-1.5 rounded-xl">
                  <span className="text-[11px] font-bold text-[#1D1D1F] flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-blue-600" />
                    <span>Per-Scene Duration:</span>
                  </span>
                  <select
                    value={targetSceneDuration}
                    onChange={(e) => setTargetSceneDuration(Number(e.target.value))}
                    className="bg-transparent text-xs font-bold text-blue-700 focus:outline-none cursor-pointer"
                  >
                    <option value={6}>6s / scene</option>
                    <option value={7}>7s / scene</option>
                    <option value={8}>8s / scene (Standard)</option>
                    <option value={9}>9s / scene</option>
                    <option value={10}>10s / scene</option>
                    <option value={12}>12s / scene</option>
                  </select>
                </div>

                <button
                  onClick={handleLoadSunoPrompt}
                  className="inline-flex items-center gap-1.5 bg-[#FFF7ED] text-[#EA580C] border border-[#FED7AA] hover:bg-[#FFEDD5] text-xs font-bold px-3.5 py-2 rounded-xl transition-all cursor-pointer"
                >
                  <Radio className="w-3.5 h-3.5" />
                  <span>Suno AI Prompt Hub</span>
                </button>

                <label className="inline-flex items-center gap-1.5 bg-[#F0FDF4] text-[#16A34A] border border-[#BBF7D0] hover:bg-[#DCFCE7] text-xs font-bold px-3.5 py-2 rounded-xl transition-all cursor-pointer">
                  <UploadCloud className="w-3.5 h-3.5" />
                  <span>{uploadingAudio ? "Uploading & Syncing..." : "Upload Suno Track (MP3/WAV)"}</span>
                  <input
                    type="file"
                    accept="audio/*"
                    onChange={handleAudioUpload}
                    disabled={uploadingAudio}
                    className="hidden"
                  />
                </label>

                <button
                  onClick={handleGenerateSong}
                  disabled={songLoading}
                  className="inline-flex items-center gap-2 bg-gradient-to-r from-[#FF6B00] to-[#EA580C] hover:opacity-95 text-white text-xs font-bold px-4 py-2 rounded-xl shadow-md shadow-orange-500/20 transition-all cursor-pointer disabled:opacity-50"
                >
                  {songLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Synthesizing...</span>
                    </>
                  ) : (
                    <>
                      <Music className="w-4 h-4" />
                      <span>Auto Synthesize</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Suno AI Music Prompt Hub Box */}
            {sunoPackage && (
              <div className="bg-[#FFFBEB] border border-[#FDE68A] rounded-2xl p-5 space-y-4 animate-in fade-in duration-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-amber-900 font-bold text-xs">
                    <Radio className="w-4 h-4 text-amber-600 animate-pulse" />
                    <span>Suno AI Music Generation Studio Hub (v3.5 / v4)</span>
                  </div>
                  <a
                    href={sunoPackage.suno_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs font-bold text-white bg-amber-600 hover:bg-amber-700 px-3 py-1.5 rounded-lg flex items-center gap-1 shadow-xs transition-all"
                  >
                    <span>Open Suno.ai Studio</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                  {/* Suno Style Prompt */}
                  <div className="bg-white border border-[#FDE68A] p-3.5 rounded-xl space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-amber-800 uppercase tracking-wider">
                        1. Suno Style of Music Prompt
                      </span>
                      <button
                        onClick={() => copySunoText(sunoPackage.style_prompt, "style")}
                        className="text-[10px] font-bold text-amber-700 hover:underline flex items-center gap-1 cursor-pointer"
                      >
                        {copiedSuno === "style" ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                        <span>{copiedSuno === "style" ? "Copied" : "Copy Prompt"}</span>
                      </button>
                    </div>
                    <p className="text-xs font-mono text-neutral-800 bg-[#FAFAFA] p-2.5 rounded-lg border border-neutral-200 leading-relaxed">
                      {sunoPackage.style_prompt}
                    </p>
                  </div>

                  {/* Suno Title */}
                  <div className="bg-white border border-[#FDE68A] p-3.5 rounded-xl space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-amber-800 uppercase tracking-wider">
                        2. Suno Song Title
                      </span>
                      <button
                        onClick={() => copySunoText(sunoPackage.suno_title, "title")}
                        className="text-[10px] font-bold text-amber-700 hover:underline flex items-center gap-1 cursor-pointer"
                      >
                        {copiedSuno === "title" ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                        <span>{copiedSuno === "title" ? "Copied" : "Copy Title"}</span>
                      </button>
                    </div>
                    <p className="text-xs font-mono font-bold text-neutral-800 bg-[#FAFAFA] p-2.5 rounded-lg border border-neutral-200">
                      {sunoPackage.suno_title}
                    </p>
                  </div>
                </div>

                {/* Suno Tagged Lyrics */}
                <div className="bg-white border border-[#FDE68A] p-3.5 rounded-xl space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-amber-800 uppercase tracking-wider">
                      3. Formatted Lyrics with Suno Structure Tags ([Verse 1], [Chorus], [Outro])
                    </span>
                    <button
                      onClick={() => copySunoText(sunoPackage.suno_lyrics, "lyrics")}
                      className="text-[10px] font-bold text-amber-700 hover:underline flex items-center gap-1 cursor-pointer"
                    >
                      {copiedSuno === "lyrics" ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                      <span>{copiedSuno === "lyrics" ? "Copied All Lyrics" : "Copy Formatted Lyrics"}</span>
                    </button>
                  </div>
                  <textarea
                    rows={6}
                    readOnly
                    value={sunoPackage.suno_lyrics}
                    className="w-full text-xs font-mono text-neutral-800 bg-[#FAFAFA] p-2.5 rounded-lg border border-neutral-200 leading-relaxed"
                  />
                </div>
              </div>
            )}

            {/* Audio Player & Analyzed Timeline Display */}
            {audioTimeline && (
              <div className="p-4.5 bg-[#FAFAFC] border border-[#E5E5EA] rounded-2xl space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <button
                      onClick={toggleAudioPlayback}
                      className="w-10 h-10 rounded-full bg-orange-500 hover:bg-orange-600 text-white flex items-center justify-center shadow-md transition-colors cursor-pointer shrink-0"
                    >
                      {isPlayingAudio ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
                    </button>
                    <div>
                      <span className="font-bold text-xs text-[#1D1D1F] block">
                        Master Nursery Song ({((audioTimeline.duration || audioTimeline.total_duration || 0)).toFixed(1)}s)
                      </span>
                      <span className="text-[11px] text-[#6E6E73]">
                        BPM: {audioTimeline.bpm || 120} • {audioTimeline.sections?.length || 0} Sections • Synchronized to Lyrics
                      </span>
                    </div>
                  </div>

                  <audio
                    ref={audioRef}
                    src={`${api.getSongAudioUrl(activeProject.id)}?t=${audioCacheBust}`}
                    onEnded={() => setIsPlayingAudio(false)}
                    className="hidden"
                  />

                  <div className="flex items-center gap-2">
                    <a
                      href={api.getSubtitlesDownloadUrl(activeProject.id)}
                      download={`${activeProject.title}.srt`}
                      className="flex items-center gap-1 text-xs font-bold text-[#EA580C] bg-[#FFF7ED] hover:bg-[#FFEDD5] border border-[#FED7AA] px-3 py-1 rounded-full transition-all"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Download Subtitles (.srt)</span>
                    </a>
                    <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Audio Timeline Synchronized</span>
                    </div>
                  </div>
                </div>

                {/* Visual Audio Sections Waveform Bar */}
                <div className="space-y-1.5">
                  <span className="text-[10px] font-bold text-[#86868B] uppercase tracking-wider">
                    Musical Section Map
                  </span>
                  <div className="w-full h-8 bg-white border border-[#E5E5EA] rounded-xl overflow-hidden flex">
                    {(audioTimeline.sections || []).map((sec, idx) => {
                      const totalDur = audioTimeline.duration || audioTimeline.total_duration || 1;
                      const widthPct = ((sec.end - sec.start) / totalDur) * 100;
                      const colors = ["bg-orange-100 text-orange-800", "bg-blue-100 text-blue-800", "bg-emerald-100 text-emerald-800", "bg-purple-100 text-purple-800"];
                      return (
                        <div
                          key={idx}
                          style={{ width: `${widthPct}%` }}
                          className={`h-full border-r border-white flex items-center justify-center text-[10px] font-bold truncate px-1 ${
                            colors[idx % colors.length]
                          }`}
                          title={`${sec.name} (${sec.start.toFixed(1)}s - ${sec.end.toFixed(1)}s)`}
                        >
                          {sec.name}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </section>
        )}

        {/* STEP 4 & 5: STORYBOARD & 3D SCENE RENDERING */}
        {activeProject && scenes.length > 0 && (
          <section className="space-y-4">
            {/* Live Rendering Progress Banner */}
            {renderLoading && (
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 animate-pulse">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-xs">
                    <Loader2 className="w-5 h-5 animate-spin" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-blue-900 block">
                      Rendering 3D Shots in Progress ({scenes.filter((s) => s.status === "COMPLETED").length} of {scenes.length} Scenes Finished)...
                    </span>
                    <span className="text-[11px] text-blue-700">
                      Storybook 3D Engine is generating camera paths, visual choreography & individual scene MP4 files.
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3 self-end sm:self-auto">
                  <div className="w-28 bg-blue-200/80 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-blue-600 h-full transition-all duration-300 rounded-full"
                      style={{
                        width: `${Math.round(((scenes.filter((s) => s.status === "COMPLETED").length || 0) / (scenes.length || 1)) * 100)}%`,
                      }}
                    />
                  </div>
                  <span className="text-xs font-mono font-bold text-blue-800">
                    {Math.round(((scenes.filter((s) => s.status === "COMPLETED").length || 0) / (scenes.length || 1)) * 100)}%
                  </span>
                </div>
              </div>
            )}

            <StoryboardView
              projectId={activeProject.id}
              scenes={scenes}
              initialSceneDuration={targetSceneDuration}
              onScenesUpdated={(updatedScenes) => setScenes(updatedScenes)}
              onSceneRerendered={async () => {
                const p = await api.getProject(activeProject.id);
                if (p) {
                  setActiveProject(p);
                  if (p.scenes) setScenes(p.scenes);
                }
              }}
            />

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={handleRenderScenes}
                disabled={renderLoading}
                className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:opacity-95 text-white text-xs font-bold px-6 py-3 rounded-xl shadow-md shadow-blue-500/20 transition-all cursor-pointer disabled:opacity-50"
              >
                {renderLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Rendering Shots ({scenes.filter((s) => s.status === "COMPLETED").length}/{scenes.length})...</span>
                  </>
                ) : (
                  <>
                    <Clapperboard className="w-4 h-4" />
                    <span>Render All 3D Scenes ({scenes.length} Shots)</span>
                  </>
                )}
              </button>
            </div>
          </section>
        )}

        {/* STEP 8: QUALITY CONTROL (QC) - Sequentially Gated */}
        {activeProject && (
          <section className="space-y-4">
            {scenes.length > 0 && (scenes.some((s) => s.status === "COMPLETED") || activeProject.status === "READY" || activeProject.status === "READY_FOR_REVIEW") ? (
              <QCCheckView
                qcResult={qcResult}
                onRerunQC={handleRunQC}
                loading={qcLoading}
              />
            ) : (
              <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 text-center space-y-2 opacity-65">
                <div className="w-8 h-8 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center mx-auto">
                  <Lock className="w-4 h-4" />
                </div>
                <h3 className="text-xs font-bold text-[#1D1D1F]">Step 8 • Quality Control (QC)</h3>
                <p className="text-[11px] text-[#6E6E73]">
                  🔒 Complete Step 4 (&quot;Render All 3D Scenes&quot;) above to unlock automated Quality Control.
                </p>
              </div>
            )}
          </section>
        )}

        {/* STEP 9 & 10: PREVIEW, APPROVE, AND YOUTUBE PRIVATE UPLOAD - Sequentially Gated */}
        {activeProject && (
          (activeProject.status === "READY" || activeProject.status === "READY_FOR_REVIEW" || (scenes.length > 0 && scenes.every((s) => s.status === "COMPLETED"))) ? (
            <section className="bg-white border border-[#E5E5EA] rounded-3xl p-6 shadow-xs space-y-6">
              <div className="space-y-1 pb-4 border-b border-[#E5E5EA]">
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                  <FileVideo className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Step 9 & 10 • Final Preview & YouTube Upload</span>
                </div>
                <h2 className="text-lg font-bold text-[#1D1D1F]">
                  Video Preview & Distribution
                </h2>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
                {/* Video Player */}
                <div className="rounded-2xl overflow-hidden bg-black aspect-video relative flex items-center justify-center border border-[#E5E5EA]">
                  <video
                    controls
                    className="w-full h-full object-cover"
                    src={`http://127.0.0.1:8000/api/v1/projects/${activeProject.id}/video`}
                    poster={`http://127.0.0.1:8000/api/v1/projects/${activeProject.id}/thumbnail`}
                  >
                    Your browser does not support the video tag.
                  </video>
                </div>

                {/* Approval & Upload Actions */}
                <div className="space-y-5">
                  <div className="space-y-2">
                    <h3 className="font-extrabold text-base text-[#1D1D1F]">{activeProject.title}</h3>
                    <p className="text-xs text-[#6E6E73] leading-relaxed">{activeProject.topic}</p>
                  </div>

                  <div className="p-4 rounded-2xl bg-[#FAFAFC] border border-[#E5E5EA] space-y-2 text-xs text-[#6E6E73]">
                    <div className="flex items-center justify-between text-[#1D1D1F] font-bold">
                      <span>Upload Status:</span>
                      <span className="text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full text-[10px]">
                        Strictly PRIVATE Default
                      </span>
                    </div>
                    <p className="text-[11px]">
                      All initial YouTube uploads are set to PRIVATE for safe creator review in YouTube Studio before public release.
                    </p>
                  </div>

                  {uploadSuccess && (
                    <div className="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-semibold flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                      <span>{uploadSuccess}</span>
                    </div>
                  )}

                  <div className="flex flex-wrap items-center gap-3 pt-2">
                    <a
                      href={`http://127.0.0.1:8000/api/v1/projects/${activeProject.id}/video`}
                      download
                      className="inline-flex items-center gap-2 bg-[#FAFAFC] hover:bg-[#F5F5F7] text-[#1D1D1F] border border-[#E5E5EA] text-xs font-bold px-5 py-3 rounded-xl transition-colors cursor-pointer"
                    >
                      <Download className="w-4 h-4" />
                      <span>Download Final MP4</span>
                    </a>

                    <button
                      onClick={handleYouTubeUpload}
                      disabled={uploadLoading}
                      className="inline-flex items-center gap-2 bg-gradient-to-r from-red-600 to-rose-600 hover:opacity-95 text-white text-xs font-bold px-6 py-3 rounded-xl shadow-md shadow-red-500/20 transition-all cursor-pointer disabled:opacity-50"
                    >
                      {uploadLoading ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span>Uploading to YouTube (Private)...</span>
                        </>
                      ) : (
                        <>
                          <UploadCloud className="w-4 h-4" />
                          <span>Upload to YouTube (Private)</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </section>
          ) : (
            <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 text-center space-y-2 opacity-65">
              <div className="w-8 h-8 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center mx-auto">
                <Lock className="w-4 h-4" />
              </div>
              <h3 className="text-xs font-bold text-[#1D1D1F]">Step 9 & 10 • Final Video Preview & YouTube Upload</h3>
              <p className="text-[11px] text-[#6E6E73]">
                🔒 Final video preview and YouTube distribution unlock once all 3D scenes finish rendering and assembling.
              </p>
            </div>
          )
        )}

        {/* Existing Projects List */}
        <div className="space-y-4 pt-6 border-t border-[#E5E5EA]">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-[#1D1D1F] tracking-tight">
              Recent Studio Productions
            </h2>
            <Link
              href="/projects"
              className="text-xs font-semibold text-[#EA580C] hover:underline flex items-center gap-1 cursor-pointer"
            >
              <span>Manage all projects</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {loading ? (
            <div className="p-8 text-center text-xs text-[#6E6E73]">Loading projects...</div>
          ) : projects.length === 0 ? (
            <div className="bg-white border border-[#E5E5EA] rounded-2xl p-12 text-center text-xs text-[#6E6E73] shadow-xs">
              No productions created yet. Click &ldquo;🔥 Find Today&apos;s Kids Topics&rdquo; above to start!
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {projects.map((proj) => (
                <div
                  key={proj.id}
                  onClick={() => {
                    setActiveProject(proj);
                    localStorage.setItem(ACTIVE_PROJ_KEY, proj.id);
                    api.getContentPackage(proj.id).then(setContentPkg).catch(() => {});
                    api.getAudioTimeline(proj.id).then(setAudioTimeline).catch(() => {});
                    api.getQCReport(proj.id).then(setQcResult).catch(() => {});
                    if (proj.scenes) setScenes(proj.scenes);
                  }}
                  className={`bg-white hover:bg-[#FAFAFC] border rounded-2xl p-5 transition-all shadow-xs group block space-y-3 cursor-pointer ${
                    activeProject?.id === proj.id ? "border-[#FF6B00] ring-2 ring-orange-500/20" : "border-[#E5E5EA]"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-[#FFF7ED] text-[#C2410C] border border-[#FED7AA]">
                      {proj.status}
                    </span>
                    <span className="text-[11px] text-[#86868B] font-medium flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(proj.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  <div>
                    <h3 className="font-bold text-[#1D1D1F] text-base group-hover:text-[#EA580C] transition-colors">
                      {proj.title}
                    </h3>
                    <p className="text-xs text-[#6E6E73] line-clamp-2 mt-1 leading-relaxed">
                      {proj.topic}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-[#E5E5EA] flex items-center justify-between text-xs text-[#6E6E73]">
                    <span>
                      {proj.video_type} • {proj.visual_style}
                    </span>
                    <span className="text-[#EA580C] font-semibold flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                      Load Into Studio →
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </>
  );
}
