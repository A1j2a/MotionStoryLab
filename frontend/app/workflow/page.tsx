"use client";

import { useEffect, useState, useRef } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { HealthData, Project, Job } from "@/lib/types";
import Link from "next/link";
import {
  Sparkles,
  Cpu,
  Layers,
  Music,
  Film,
  CheckCircle2,
  Clock,
  ArrowRight,
  RefreshCw,
  Terminal,
  ExternalLink,
  Zap,
  HardDrive,
  Sliders,
  ChevronRight,
  Bot,
  Box,
  Volume2,
  Tv,
  UploadCloud,
  Activity,
  Play,
  Loader2,
  Check,
  Flame,
} from "lucide-react";

const ACTIVE_PROJ_KEY = "motionstory_active_project_id";

export default function WorkflowEnginePage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState<string>("ollama");
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [activeJob, setActiveJob] = useState<Job | null>(null);

  const fetchHealthAndProject = async () => {
    setLoading(true);
    try {
      const h = await api.getHealth();
      setHealth(h);

      const activeId = localStorage.getItem(ACTIVE_PROJ_KEY);
      if (activeId) {
        const p = await api.getProject(activeId);
        setActiveProject(p);
        if (p && p.jobs && p.jobs.length > 0) {
          setActiveJob(p.jobs[0]);
        }
      } else {
        const list = await api.getProjects();
        if (list && list.length > 0) {
          setActiveProject(list[0]);
          if (list[0].jobs && list[0].jobs.length > 0) {
            setActiveJob(list[0].jobs[0]);
          }
        }
      }
    } catch {
      // offline
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthAndProject();
    const interval = setInterval(fetchHealthAndProject, 4000);
    return () => clearInterval(interval);
  }, []);

  // Compute active stage (1 to 6) based on active project state
  const computeActiveStage = (): number => {
    if (!activeProject) return 1;
    const s = activeProject.status;
    const js = activeJob?.status || "";
    const cs = activeJob?.current_step || "";

    if (s === "READY" || s === "READY_FOR_REVIEW" || js === "READY_FOR_REVIEW" || cs === "READY_FOR_PREVIEW_AND_QC") return 6;
    if (s === "COMPOSITING" || js === "ASSEMBLING" || cs === "FINAL_ASSEMBLY") return 5;
    if (s === "RENDERING" || js === "SCENE_RENDERING" || cs.startsWith("RENDERED_SCENE")) return 4;
    if (s === "AUDIO_GENERATION" || js === "AUDIO_GENERATION" || cs === "STORYBOARD_READY") return 3;
    if (s === "CHARACTER_DESIGN" || cs === "CHARACTER_DESIGN") return 2;
    return 1;
  };

  const currentStage = computeActiveStage();

  const PIPELINE_NODES = [
    {
      id: "ollama",
      stageNum: 1,
      title: "OpenRouter / Local AI",
      subtitle: "Story, Lyrics & Concept Engine",
      port: "http://127.0.0.1:11434",
      status: health?.ollama?.status === "connected" ? "connected" : "standby",
      icon: Bot,
      role: "Rhyming Lyrics & Preschool Storyboard Planner",
      tech: "OpenRouter (Llama 3.3/Gemini) & Local Ollama Metal",
      color: "#FF6B00",
      inputs: [
        "Preschool Theme (e.g., Yellow School Bus)",
        "Target Age: 1-5 Years",
        "Rhyme Meter: AABB Classic Preschool Rhyme Structure",
      ],
      outputs: [
        "Structured Verses & Onomatopoeia Tags",
        "Character Visual Bible JSON",
        "High-CTR YouTube Title & Tags",
      ],
      description: "Researches viral engagement signals, constructs sing-along rhymes with toddler repetitive cadence, and plans structured camera choreographies.",
      launchCmd: "ollama run llama3.2",
    },
    {
      id: "character_studio",
      stageNum: 2,
      title: "3D Character Studio",
      subtitle: "Procedural Geometry & Rigging",
      port: "Storybook 3D / ComfyUI (8188)",
      status: "connected",
      icon: Box,
      role: "Dynamic 3D Geometry & Facial Rigging",
      tech: "Storybook 3D API & Cartoon Shading",
      color: "#3B82F6",
      inputs: [
        "Character Bible JSON",
        "Color Harmony Palette",
        "Glossy Cartoon Material Settings",
      ],
      outputs: [
        "Procedural 3D Character Meshes",
        "Expressive Eyes with Reflections",
        "Modular Stage Props (Beds, Clouds, Cars)",
      ],
      description: "Constructs procedural 3D preschool character meshes tailored specifically to the project theme with smooth rounded geometry and vibrant candy hues.",
      launchCmd: "python3 -m renderer.storybook_engine",
    },
    {
      id: "audio_studio",
      stageNum: 3,
      title: "Nursery Audio Orchestrator",
      subtitle: "Suno AI & Neural DSP Engine",
      port: "Kokoro (8880) + Suno Audio Hub",
      status: health?.tts?.status === "connected" ? "connected" : "standby",
      icon: Volume2,
      role: "Multi-Track Music & Karaoke Sync",
      tech: "Suno AI / Kokoro Neural Voice + FFmpeg DSP",
      color: "#10B981",
      inputs: [
        "Formatted Lyric Stanzas ([Verse], [Chorus])",
        "120-128 BPM Preschool Bounce Rhythm",
        "Suno Style Prompt Package",
      ],
      outputs: [
        "master_soundtrack.wav (Stereo Mix)",
        "subtitles.srt (Karaoke Subtitles)",
        "Exact Beat Timeline Alignment (ms)",
      ],
      description: "Produces high-energy toddler sing-along tracks with balanced chime orchestration and generates millisecond-accurate karaoke SRT subtitle sync.",
      launchCmd: "docker run -p 8880:8880 ghcr.io/resemble-ai/kokoro-fastapi",
    },
    {
      id: "metal_render",
      stageNum: 4,
      title: "Headless 3D Render Engine",
      subtitle: "Wan FLF2V / Storybook 3D",
      port: "Wan 2.1 FLF2V / FFmpeg",
      status: "connected",
      icon: Tv,
      role: "AI 3D Video & Shot Cinematics",
      tech: "Wan FLF2V & Metal FFmpeg Canvas",
      color: "#8B5CF6",
      inputs: [
        "Shot Sequence Timeline",
        "Camera Choreography (Wide, Close, Orbit, Tracking)",
        "Pixar 3-Point Studio Soft Lighting",
      ],
      outputs: [
        "scene_001.mp4 (Establishing Panoramic Shot)",
        "scene_002.mp4 (Dynamic Action Track)",
        "scene_003.mp4 (Hero Character Smile & Wave)",
      ],
      description: "Renders 1280x720 24fps frames headlessly using Wan FLF2V AI video generation or Local Storybook 3D with distinct camera choreography for each musical phrase.",
      launchCmd: "python3 -m renderer.storybook_engine --scene-config scene_config.json",
    },
    {
      id: "ffmpeg_master",
      stageNum: 5,
      title: "Master AV Compositor",
      subtitle: "FFmpeg 7.1 Multi-Track Engine",
      port: "/opt/homebrew/bin/ffmpeg",
      status: "connected",
      icon: Film,
      role: "Multi-Track Stitching & Subtitle Burning",
      tech: "FFmpeg libx264, AAC & ASS Subtitle Filter",
      color: "#EC4899",
      inputs: [
        "Rendered 3D Scene Clips (MP4)",
        "master_soundtrack.wav (Stereo 44.1kHz)",
        "subtitles.srt (Karaoke Timestamps)",
      ],
      outputs: [
        "final.mp4 (Broadcast 720p/1080p Video)",
        "thumbnail.jpg (High-CTR 3D Video Cover)",
      ],
      description: "Sequences all camera shots, burns drop-shadow toddler subtitles, balances audio gain, and compiles broadcast-ready final MP4.",
      launchCmd: "ffmpeg -y -i scenes -i master.wav -c:v libx264 final.mp4",
    },
    {
      id: "n8n_youtube",
      stageNum: 6,
      title: "Distribution & Quality Control",
      subtitle: "QC Guard & YouTube Upload",
      port: "http://127.0.0.1:5678",
      status: health?.n8n?.status === "connected" ? "connected" : "standby",
      icon: UploadCloud,
      role: "QC Audio/Video Audit & YouTube Release",
      tech: "Automated QC Engine & YouTube Data API v3",
      color: "#F59E0B",
      inputs: [
        "final.mp4 & thumbnail.jpg",
        "High-CTR SEO Metadata JSON",
        "Strict Private Review Privacy Flag",
      ],
      outputs: [
        "Quality Control Pass Certificate",
        "YouTube Studio Private Upload with SEO Tags",
      ],
      description: "Runs automated verification on audio loudness and black frames, and publishes directly to YouTube in creator private review mode.",
      launchCmd: "npx n8n start --port 5678",
    },
  ];

  const activeNode = PIPELINE_NODES.find((n) => n.id === selectedNode) || PIPELINE_NODES[0];

  return (
    <>
      <style jsx global>{`
        @keyframes workflowDash {
          from { stroke-dashoffset: 36; }
          to { stroke-dashoffset: 0; }
        }
        .animate-workflow-line {
          stroke-dasharray: 8 6;
          animation: workflowDash 1.2s linear infinite;
        }
        .idle-workflow-line {
          stroke-dasharray: 4 4;
        }
      `}</style>

      <Header
        title="Live Engine Workflow Architecture"
        subtitle="Visual interactive schematic of local AI planning, procedural 3D synthesis, and real-time GPU pipelines"
      />

      <main className="p-8 space-y-8 flex-1 max-w-7xl mx-auto w-full">
        {/* Top Live Engine & Active Project Monitor */}
        <div className="bg-white border border-[#E5E5EA] p-5 rounded-2xl shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-11 h-11 rounded-2xl bg-[#FFF7ED] border border-[#FED7AA] flex items-center justify-center text-[#EA580C] shadow-xs">
              <Activity className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-[#1D1D1F]">
                  Live Engine Pipeline Monitor
                </h2>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600 border border-emerald-200 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span>
                  LIVE ENGINE ACTIVE
                </span>
              </div>
              <p className="text-xs text-[#6E6E73] mt-0.5">
                {activeProject ? (
                  <span>
                    Current Production: <strong className="text-[#1D1D1F]">&ldquo;{activeProject.title}&rdquo;</strong> • Step: <span className="text-[#EA580C] font-semibold">{activeJob?.current_step || activeProject.status}</span>
                  </span>
                ) : (
                  <span>No active production running. Pick a topic on Dashboard to start the engine flow.</span>
                )}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            {activeProject && (
              <Link
                href="/"
                className="inline-flex items-center gap-1.5 bg-gradient-to-r from-[#FF6B00] to-[#EA580C] hover:opacity-95 text-white text-xs font-bold px-4 py-2 rounded-xl shadow-xs transition-all"
              >
                <span>Open Dashboard</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            )}
            <button
              onClick={fetchHealthAndProject}
              disabled={loading}
              className="inline-flex items-center gap-1.5 bg-[#F5F5F7] hover:bg-[#E5E5EA] text-[#1D1D1F] border border-[#E5E5EA] text-xs font-semibold px-3.5 py-2 rounded-xl transition-all cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-[#FF6B00]" : ""}`} />
              <span>Ping Nodes</span>
            </button>
          </div>
        </div>

        {/* ============================================================== */}
        {/* DYNAMIC PIPELINE SCHEMATIC (WITH ANIMATED WORKFLOW CONDUITS) */}
        {/* ============================================================== */}
        <div className="bg-white border border-[#E5E5EA] rounded-3xl p-7 shadow-xs relative overflow-hidden space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center gap-2 text-xs font-bold text-[#1D1D1F] uppercase tracking-wider">
              <Zap className="w-4 h-4 text-[#FF6B00]" />
              <span>Interactive Pipeline Conduits • Live Stage Highlighting</span>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                <span className="text-[11px] text-[#6E6E73]">Completed</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-orange-500 animate-ping"></span>
                <span className="text-[11px] font-bold text-orange-600">Active Flow</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-slate-300"></span>
                <span className="text-[11px] text-[#86868B]">Standby</span>
              </div>
            </div>
          </div>

          {/* SVG Animated Connector Graphic between Row 1 and Row 2 */}
          <div className="relative">
            {/* Grid of 6 Nodes */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
              {PIPELINE_NODES.map((node) => {
                const isSelected = selectedNode === node.id;
                const isCurrentActive = currentStage === node.stageNum;
                const isFinished = currentStage > node.stageNum;
                const Icon = node.icon;

                return (
                  <div
                    key={node.id}
                    onClick={() => setSelectedNode(node.id)}
                    className={`p-5 rounded-2xl border transition-all cursor-pointer relative bg-white ${
                      isCurrentActive
                        ? "border-[#FF6B00] ring-4 ring-orange-500/20 shadow-lg shadow-orange-500/10 scale-[1.02]"
                        : isFinished
                        ? "border-emerald-300 bg-emerald-50/15 hover:shadow-xs"
                        : isSelected
                        ? "border-blue-500 ring-2 ring-blue-500/20 shadow-xs"
                        : "border-[#E5E5EA] hover:border-[#D1D1D6] hover:shadow-xs"
                    }`}
                  >
                    {/* Active Pulsing Ribbon */}
                    {isCurrentActive && (
                      <div className="absolute -top-3 left-4 bg-gradient-to-r from-[#FF6B00] to-[#EA580C] text-white text-[9px] font-extrabold uppercase px-2.5 py-0.5 rounded-full shadow-xs flex items-center gap-1">
                        <Loader2 className="w-2.5 h-2.5 animate-spin" />
                        <span>CURRENT ACTIVE STAGE</span>
                      </div>
                    )}

                    <div className="flex items-center justify-between mb-3 mt-1">
                      <div
                        className="w-10 h-10 rounded-xl flex items-center justify-center shadow-xs"
                        style={{ backgroundColor: `${node.color}15`, color: node.color }}
                      >
                        <Icon className="w-5 h-5" />
                      </div>
                      <div className="flex items-center gap-1.5">
                        {isFinished ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                            <Check className="w-3 h-3" />
                            <span>DONE</span>
                          </span>
                        ) : isCurrentActive ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-orange-100 text-orange-800 animate-pulse">
                            <span className="w-1.5 h-1.5 rounded-full bg-orange-600 animate-ping"></span>
                            <span>PROCESSING</span>
                          </span>
                        ) : (
                          <span className="text-[10px] font-semibold text-[#86868B] font-mono bg-slate-100 px-2 py-0.5 rounded-full">
                            STANDBY
                          </span>
                        )}
                      </div>
                    </div>

                    <span className="text-[10px] font-mono font-bold text-[#FF6B00] block mb-1">
                      STAGE 0{node.stageNum}
                    </span>
                    <h3 className="text-sm font-bold text-[#1D1D1F] leading-tight">
                      {node.title}
                    </h3>
                    <p className="text-xs text-[#6E6E73] mt-1 font-medium line-clamp-1">
                      {node.role}
                    </p>

                    <div className="pt-3 mt-3 border-t border-[#F5F5F7] flex items-center justify-between text-[11px] text-[#86868B]">
                      <span className="truncate max-w-[140px] font-mono text-[10px]">
                        {node.port}
                      </span>
                      <span className="text-[#FF6B00] font-semibold flex items-center gap-1">
                        Inspect <ChevronRight className="w-3 h-3" />
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Animated Conduit Status Bar */}
          <div className="mt-6 pt-5 border-t border-[#E5E5EA] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-[#6E6E73] bg-[#FAFAFC] -mx-7 -mb-7 p-4 px-7">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
              <span className="font-semibold text-[#1D1D1F]">
                Continuous Signal Flow:
              </span>
              <span className="text-[11px]">
                Stage 01 (Topics/Lyrics) ➔ Stage 02 (3D Characters) ➔ Stage 03 (Suno Audio) ➔ Stage 04 (Wan/3D Engine) ➔ Stage 05 (FFmpeg) ➔ Stage 06 (YouTube)
              </span>
            </div>
            <span className="font-mono text-[11px] text-[#86868B]">
              Pipeline: Zero-Cloud Apple Silicon M4 Local Stack
            </span>
          </div>
        </div>

        {/* Selected Node Detailed Inspector */}
        <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 shadow-xs space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E5E5EA]">
            <div className="flex items-center gap-3.5">
              <div
                className="w-11 h-11 rounded-xl flex items-center justify-center shadow-xs"
                style={{ backgroundColor: `${activeNode.color}15`, color: activeNode.color }}
              >
                <activeNode.icon className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-base font-bold text-[#1D1D1F]">{activeNode.title}</h3>
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-[#FFF7ED] text-[#C2410C] border border-[#FED7AA]">
                    STAGE 0{activeNode.stageNum}
                  </span>
                </div>
                <p className="text-xs text-[#6E6E73]">{activeNode.subtitle}</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-semibold px-3 py-1 rounded-xl bg-[#F5F5F7] border border-[#E5E5EA] text-[#1D1D1F]">
                Endpoint: {activeNode.port}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left: Functional Specs & Architecture */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold text-[#1D1D1F] uppercase tracking-wider">
                Engine Architectural Role
              </h4>
              <p className="text-xs text-[#6E6E73] leading-relaxed bg-[#FAFAFC] border border-[#E5E5EA] p-4 rounded-xl font-medium">
                {activeNode.description}
              </p>

              <div className="space-y-2">
                <span className="text-[11px] font-bold text-[#1D1D1F] block">Direct Daemon Command</span>
                <div className="bg-[#1D1D1F] text-emerald-400 font-mono text-xs p-3 rounded-xl flex items-center justify-between">
                  <span className="truncate">$ {activeNode.launchCmd}</span>
                  <Terminal className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                </div>
              </div>
            </div>

            {/* Right: Inputs & Outputs Data Contracts */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold text-[#1D1D1F] uppercase tracking-wider">
                Pipeline Data Contracts (I/O)
              </h4>

              <div className="space-y-3">
                <div className="bg-[#FAFAFC] border border-[#E5E5EA] p-3.5 rounded-xl space-y-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#FF6B00] block">
                    Inbound Input Stream
                  </span>
                  <ul className="text-xs text-[#6E6E73] space-y-1 list-disc list-inside">
                    {activeNode.inputs.map((inp, idx) => (
                      <li key={idx}>{inp}</li>
                    ))}
                  </ul>
                </div>

                <div className="bg-[#FAFAFC] border border-[#E5E5EA] p-3.5 rounded-xl space-y-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-600 block">
                    Outbound Generated Artifacts
                  </span>
                  <ul className="text-xs text-[#6E6E73] space-y-1 list-disc list-inside">
                    {activeNode.outputs.map((out, idx) => (
                      <li key={idx}>{out}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
