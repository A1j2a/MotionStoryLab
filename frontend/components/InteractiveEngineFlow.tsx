"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import {
  Sparkles,
  Bot,
  Music,
  Film,
  Tv,
  UploadCloud,
  CheckCircle2,
  Layers,
  Cpu,
  Clock,
  ArrowRight,
  RefreshCw,
  Sliders,
  GitBranch,
  Play,
  Pause,
  Loader2,
  Check,
  Zap,
  Palette,
  FileText,
  Activity,
  Terminal,
  ExternalLink,
  ChevronRight,
  Info,
  Maximize2,
  Volume2,
  Compass,
} from "lucide-react";
import { api, API_BASE } from "@/lib/api";
import { HealthData, Project, Job } from "@/lib/types";

export interface EngineNodeData {
  id: string;
  stepNumber?: number;
  category: "input" | "core" | "condition" | "branch" | "output";
  title: string;
  subtitle: string;
  icon: any;
  iconBg: string;
  iconColor: string;
  aiEngine: string;
  aiBadge: string;
  modelSlug: string;
  endpoint: string;
  role: string;
  aiActionDetails: string[];
  inputs: string[];
  outputs: string[];
  status: "completed" | "running" | "ready" | "standby";
  metrics: { label: string; value: string }[];
  actionLink?: { label: string; href: string };
}

interface InteractiveEngineFlowProps {
  activeProjectId?: string;
  onSelectProject?: (id: string) => void;
  compact?: boolean;
}

export function InteractiveEngineFlow({
  activeProjectId,
  compact = false,
}: InteractiveEngineFlowProps) {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [activeJob, setActiveJob] = useState<Job | null>(null);
  const [hoveredNode, setHoveredNode] = useState<EngineNodeData | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string>("core_lyrics");
  const [cursorPos, setCursorPos] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [simulatedStage, setSimulatedStage] = useState<number>(1);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const containerRef = useRef<HTMLDivElement | null>(null);

  // Fetch health & project
  const loadData = async () => {
    setRefreshing(true);
    try {
      const h = await api.getHealth().catch(() => null);
      if (h) setHealth(h);

      const targetId =
        activeProjectId ||
        (typeof window !== "undefined"
          ? localStorage.getItem("motionstory_active_project_id")
          : null);

      if (targetId) {
        const p = await api.getProject(targetId).catch(() => null);
        if (p) {
          setActiveProject(p);
          if (p.jobs && p.jobs.length > 0) setActiveJob(p.jobs[0]);
        }
      } else {
        const list = await api.getProjects().catch(() => []);
        if (list && list.length > 0) {
          setActiveProject(list[0]);
          if (list[0].jobs && list[0].jobs.length > 0) setActiveJob(list[0].jobs[0]);
        }
      }
    } catch {
      // offline
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, [activeProjectId]);

  // Simulation loop when user clicks "Run Engine Simulation"
  useEffect(() => {
    if (!isSimulating) return;
    const simTimer = setInterval(() => {
      setSimulatedStage((prev) => (prev >= 6 ? 1 : prev + 1));
    }, 2800);
    return () => clearInterval(simTimer);
  }, [isSimulating]);

  // Compute live active stage
  const computeActiveStage = (): number => {
    if (isSimulating) return simulatedStage;
    if (!activeProject) return 1;
    const s = activeProject.status;
    const js = activeJob?.status || "";
    const cs = activeJob?.current_step || "";

    if (
      s === "READY" ||
      s === "READY_FOR_REVIEW" ||
      js === "READY_FOR_REVIEW" ||
      cs === "READY_FOR_PREVIEW_AND_QC"
    )
      return 6;
    if (s === "COMPOSITING" || js === "ASSEMBLING" || cs === "FINAL_ASSEMBLY") return 5;
    if (s === "RENDERING" || js === "SCENE_RENDERING" || cs.startsWith("RENDERED_SCENE"))
      return 4;
    if (s === "AUDIO_GENERATION" || js === "AUDIO_GENERATION" || cs === "STORYBOARD_READY")
      return 3;
    if (s === "CHARACTER_DESIGN" || cs === "CHARACTER_DESIGN") return 2;
    return 1;
  };

  const currentStage = computeActiveStage();

  // Nodes definition representing the complete pipeline architecture
  const INPUT_NODES: EngineNodeData[] = [
    {
      id: "seed_topic",
      category: "input",
      title: "Viral Topic & Rhyme Seed",
      subtitle: "Preschool Engagement Research",
      icon: Sparkles,
      iconBg: "bg-[#1E293B]",
      iconColor: "text-amber-400",
      aiEngine: "OpenRouter Deep Research / Llama 3.3",
      aiBadge: "LLM Topic Agent",
      modelSlug: "deepseek/deepseek-r1:free",
      endpoint: "https://openrouter.ai/api/v1",
      role: "Researches viral toddler sing-along hooks, repetitive cadence, and phonics.",
      aiActionDetails: [
        "Analyzes preschool YouTube search signals & nursery rhyme retention metrics.",
        "Generates 6 thematic rhyme concepts with repetitive preschool hooks.",
        "Calculates target engagement age bracket (1 to 5 years).",
      ],
      inputs: ["User Keyword / Topic Input", "Target Age: Toddler/Preschool", "Language: en"],
      outputs: ["Core Story Theme", "Educational Phonics Angle", "High-CTR Rhyme Title"],
      status: "completed",
      metrics: [
        { label: "Target Age", value: "1-5 Yrs" },
        { label: "Cadence", value: "AABB Meter" },
      ],
      actionLink: { label: "Explore Topics", href: "/create" },
    },
    {
      id: "seed_style",
      category: "input",
      title: "Visual Bible & Palette Directive",
      subtitle: "3D Disney/Pixar Standards",
      icon: Palette,
      iconBg: "bg-[#1E293B]",
      iconColor: "text-sky-400",
      aiEngine: "Style Enforcement Engine",
      aiBadge: "Pixar 3D Standard",
      modelSlug: "Unreal Engine 5 / Octane Render Style",
      endpoint: "Internal Visual Bible Module",
      role: "Dictates color harmony, soft studio 3-point lighting, and glossy cartoon materials.",
      aiActionDetails: [
        "Sets saturated candy hues (Sky Turquoise, Sunshine Yellow, Bubblegum Pink).",
        "Enforces soft diffuse studio rim lighting with warm highlights.",
        "Prevents realistic human faces; mandates rounded cartoon character proportions.",
      ],
      inputs: ["Style Preset: 3D Cartoon Stylized", "Aspect Ratio: 16:9 Landscape"],
      outputs: ["Visual Style Matrix", "Lighting Presets", "Environment Palette Rules"],
      status: "completed",
      metrics: [
        { label: "Style", value: "3D Pixar CGI" },
        { label: "Aspect", value: "16:9 Landscape" },
      ],
      actionLink: { label: "Character Bible", href: "/characters" },
    },
    {
      id: "seed_audio",
      category: "input",
      title: "Preschool Tempo & Rhythm Seed",
      subtitle: "120-128 BPM Sing-Along Grid",
      icon: Volume2,
      iconBg: "bg-[#1E293B]",
      iconColor: "text-emerald-400",
      aiEngine: "Neural Rhythm Analyzer",
      aiBadge: "BPM Synthesizer",
      modelSlug: "Preschool DSP Grid (124 BPM)",
      endpoint: "Internal Audio Rules Engine",
      role: "Establishes rhythmic beat grid for song generation and karaoke subtitle sync.",
      aiActionDetails: [
        "Calibrates 120-128 BPM bounce tempo ideal for toddler clapping & dancing.",
        "Allocates 8 to 18 distinct musical beats matching animated scene cuts.",
        "Pre-configures chime, marimba, and acoustic preschool instrument layers.",
      ],
      inputs: ["Target Video Duration (1.5 - 5 min)", "Toddler Energy Profile: High Bounce"],
      outputs: ["BPM Grid (124 BPM)", "Measure Timing Arrays", "Karaoke Timestamp Grid"],
      status: "completed",
      metrics: [
        { label: "BPM", value: "124 BPM" },
        { label: "Meter", value: "4/4 Bounce" },
      ],
      actionLink: { label: "Audio Studio", href: "/audio" },
    },
  ];

  const CORE_NODES: EngineNodeData[] = [
    {
      id: "core_lyrics",
      stepNumber: 1,
      category: "core",
      title: "Lyrics & Storyboard Synthesizer",
      subtitle: "AABB Verses & Scene Beat Breakdown",
      icon: FileText,
      iconBg: "bg-[#1E293B]",
      iconColor: "text-amber-400",
      aiEngine: "OpenRouter LLM + Local Ollama (Port 11434)",
      aiBadge: "Llama 3.2 / DeepSeek-R1",
      modelSlug: "llama3.2 / deepseek-r1",
      endpoint: "http://127.0.0.1:11434/api/generate",
      role: "Creates full original rhyming lyrics and maps them to 18 animated camera scenes.",
      aiActionDetails: [
        "Synthesizes 100% original preschool lyrics with onomatopoeia (beep beep, splash splash).",
        "Divides complete song into structured 5 to 8 second scene visual prompts.",
        "Specifies camera motion choreography for each scene (Tracking, Low-Angle, Orbit, Close-Up).",
      ],
      inputs: ["Topic & Rhyme Seed", "Duration Directive", "Character Description"],
      outputs: ["Structured Lyrics JSON", "18x Scene Visual Prompts", "Camera Direction Matrix"],
      status: currentStage >= 1 ? (currentStage === 1 ? "running" : "completed") : "ready",
      metrics: [
        { label: "Total Scenes", value: "18 Scenes" },
        { label: "Rhyme Scheme", value: "AABB Metric" },
      ],
      actionLink: { label: "Scene Editor", href: "/scenes" },
    },
    {
      id: "core_character",
      stepNumber: 2,
      category: "core",
      title: "3D Character Consistency Studio",
      subtitle: "Character Turnaround & Mesh Rigging",
      icon: Layers,
      iconBg: "bg-[#1E293B]",
      iconColor: "text-blue-400",
      aiEngine: "Fal.ai Flux / Local 3D Turnaround Generator",
      aiBadge: "Flux Dev / LoRA Consistency",
      modelSlug: "fal-ai/flux/dev",
      endpoint: "https://fal.run/fal-ai/flux/dev",
      role: "Maintains 100% facial and appearance identity of characters across every scene.",
      aiActionDetails: [
        "Generates 3D multi-angle character turnaround reference images.",
        "Locks character clothing, color palette, and facial expression anchors.",
        "Produces character prompt embeddings injected into all video scenes.",
      ],
      inputs: ["Character Appearance Prompt", "3D Pixar Visual Bible", "Color Tokens"],
      outputs: ["character_bible.json", "Hero Character Turnaround Reference", "Prompt Embeddings"],
      status: currentStage >= 2 ? (currentStage === 2 ? "running" : "completed") : "standby",
      metrics: [
        { label: "Identity Lock", value: "100% Strict" },
        { label: "Render", value: "3D Pixar" },
      ],
      actionLink: { label: "Character Bible", href: "/characters" },
    },
    {
      id: "core_audio",
      stepNumber: 3,
      category: "core",
      title: "Neural Audio & Karaoke Sync",
      subtitle: "Suno AI Music & Subtitles SRT",
      icon: Music,
      iconBg: "bg-[#1E293B]",
      iconColor: "text-emerald-400",
      aiEngine: "Suno AI v3.5 / Kokoro Neural Voice + FFmpeg DSP",
      aiBadge: "Neural Audio + Subtitles",
      modelSlug: "suno-v3.5 / kokoro-fastapi",
      endpoint: "http://127.0.0.1:8880 + Suno Audio Hub",
      role: "Produces vocal song soundtrack and aligns word-level millisecond SRT subtitles.",
      aiActionDetails: [
        "Synthesizes full melodic vocal preschool song with joyful upbeat accompaniment.",
        "Performs neural phoneme time-alignment for millisecond-accurate karaoke subtitles.",
        "Exports master_soundtrack.wav (Stereo 44.1kHz) and subtitles.srt with drop-shadow tags.",
      ],
      inputs: ["Full Song Lyrics", "BPM Directive: 124 BPM", "Instrumental Preset: Chime Pop"],
      outputs: ["master_soundtrack.wav", "subtitles.srt (Karaoke Sync)", "Vocal/Inst Stems"],
      status: currentStage >= 3 ? (currentStage === 3 ? "running" : "completed") : "standby",
      metrics: [
        { label: "Format", value: "WAV 44.1kHz" },
        { label: "Sync Accuracy", value: "±20ms SRT" },
      ],
      actionLink: { label: "Audio Studio", href: "/audio" },
    },
  ];

  const CONDITION_NODE: EngineNodeData = {
    id: "condition_routing",
    stepNumber: 4,
    category: "condition",
    title: "Scene Production Routing Condition",
    subtitle: "AI Video vs Creator Upload Mode",
    icon: GitBranch,
    iconBg: "bg-[#2A2B2E]",
    iconColor: "text-purple-400",
    aiEngine: "Autonomous Dispatcher & Validator",
    aiBadge: "Condition Branch",
    modelSlug: "Pipeline Decision Matrix",
    endpoint: "Internal Task Router",
    role: "Evaluates whether scenes are autonomously rendered by Wan AI or uploaded by creator.",
    aiActionDetails: [
      "Branch A (Wan AI Video Engine): When FAL_KEY is active, generates 3D scenes autonomously.",
      "Branch B (Creator Upload Studio): When creator uploads MP4s, auto-validates and sequences clips.",
      "Validates resolution, duration, FPS, and prevents black-frame drops.",
    ],
    inputs: ["18x Scene Prompts", "Scene Duration Arrays", "Creator Upload Watcher"],
    outputs: ["Route Selection", "Validated Scene Manifest", "Frame Buffer Sequence"],
    status: currentStage >= 4 ? (currentStage === 4 ? "running" : "completed") : "standby",
    metrics: [
      { label: "Branches", value: "AI or Manual" },
      { label: "Resolution", value: "720p / 1080p" },
    ],
    actionLink: { label: "Manual Studio", href: "/studio" },
  };

  const BRANCH_NODES: EngineNodeData[] = [
    {
      id: "branch_wan",
      category: "branch",
      title: "Wan 2.1 FLF2V AI Video Generator",
      subtitle: "First-to-Last Frame 3D Animation",
      icon: Film,
      iconBg: "bg-[#1E293B]",
      iconColor: "text-purple-400",
      aiEngine: "Fal.ai Wan 2.1 Video Provider",
      aiBadge: "fal-ai/wan-flf2v",
      modelSlug: "fal-ai/wan-flf2v",
      endpoint: "https://fal.run/fal-ai/wan-flf2v",
      role: "Generates 720p 24fps 3D animated scene videos with camera choreography.",
      aiActionDetails: [
        "Translates scene JSON into Wan First-Frame to Last-Frame generation payloads.",
        "Executes camera pans, tracking shots, and character smiling/waving movements.",
        "Applies negative prompts to strictly exclude real humans, dark tones, and distortion.",
      ],
      inputs: ["Scene Prompts", "Character Turnaround", "Negative Prompt Filter"],
      outputs: ["scene_001.mp4 to scene_018.mp4", "Start/End Keyframes", "Motion Vectors"],
      status: currentStage >= 4 ? (currentStage === 4 ? "running" : "completed") : "standby",
      metrics: [
        { label: "Resolution", value: "720p 24fps" },
        { label: "Frames", value: "81 Frames/Shot" },
      ],
      actionLink: { label: "Render Pipeline", href: "/render" },
    },
    {
      id: "branch_upload",
      category: "branch",
      title: "Creator Upload & Sequence Engine",
      subtitle: "Timestamp Mapper & Scene Matcher",
      icon: UploadCloud,
      iconBg: "bg-[#1E293B]",
      iconColor: "text-blue-400",
      aiEngine: "AI Prober & Sequence Validator",
      aiBadge: "Auto-Sequencer",
      modelSlug: "FFprobe Media Inspector",
      endpoint: "/opt/homebrew/bin/ffprobe",
      role: "Inspects uploaded video clips, matches scene numbers, and adjusts durations.",
      aiActionDetails: [
        "Auto-detects scene files (scene_01.mp4) or unresolved clips uploaded by creator.",
        "Probes video duration, frame rates, and pads/scales clips to match song beats.",
        "Provides 1-click sequence confirmation and order swapping UI.",
      ],
      inputs: ["Uploaded MP4/MOV Clips", "Target Scene Durations", "Sequence Confirmation"],
      outputs: ["Mapped Scene Clips", "Verified Timing Manifest", "Assembly Readiness Flag"],
      status: currentStage >= 4 ? (currentStage === 4 ? "running" : "completed") : "standby",
      metrics: [
        { label: "Tolerance", value: "Auto-Scale" },
        { label: "Supported", value: "MP4, MOV, WebM" },
      ],
      actionLink: { label: "Upload Studio", href: "/studio" },
    },
  ];

  const COMPOSITOR_NODE: EngineNodeData = {
    id: "core_compositor",
    stepNumber: 5,
    category: "core",
    title: "Master AV Compositor & Multiplexer",
    subtitle: "FFmpeg 7.1 Multi-Track Engine",
    icon: Cpu,
    iconBg: "bg-[#1E293B]",
    iconColor: "text-pink-400",
    aiEngine: "FFmpeg 7.1 Multi-Track Compositor",
    aiBadge: "libx264 + AAC + FilterComplex",
    modelSlug: "FFmpeg 7.1 HW Accelerated",
    endpoint: "/opt/homebrew/bin/ffmpeg",
    role: "Stitches scenes, mixes clip audio + song simultaneously, and burns animated subtitles.",
    aiActionDetails: [
      "Multi-Track Audio: Plays scene background sounds and generated song simultaneously.",
      "Karaoke Subtitles: Burns drop-shadow toddler lyrics smoothly at bottom of video.",
      "Dynamic Channel Branding: Overlays channel logo using customizable bottom spacing slider.",
      "Seamless Transitions: Merges intro/outro branding without muting scene soundtrack.",
    ],
    inputs: [
      "18x Rendered Scene Videos",
      "master_soundtrack.wav",
      "subtitles.srt",
      "Channel Watermark Logo",
    ],
    outputs: ["final.mp4 (Broadcast Video)", "Video Timeline Manifest", "QC Log"],
    status: currentStage >= 5 ? (currentStage === 5 ? "running" : "completed") : "standby",
    metrics: [
      { label: "Codec", value: "H.264 / AAC" },
      { label: "Subtitles", value: "Burned ASS/SRT" },
    ],
    actionLink: { label: "Approval & Preview", href: "/approval" },
  };

  const THUMBNAIL_NODE: EngineNodeData = {
    id: "core_thumbnail",
    stepNumber: 6,
    category: "core",
    title: "High-CTR 3D Thumbnail & SEO Suite",
    subtitle: "Topic-Aligned AI Prompt & Compact 3D Typography",
    icon: Sparkles,
    iconBg: "bg-[#1E293B]",
    iconColor: "text-amber-500",
    aiEngine: "Topic-Aligned 3D Pixar AI Prompt Engine",
    aiBadge: "3D Pixar / Flux Prompt",
    modelSlug: "fal-ai/flux/dev + Midjourney v6 Prompt",
    endpoint: "Internal High-CTR Compositor",
    role: "Generates topic-based 3D Pixar cover prompt (never video frame) with compact candy title.",
    aiActionDetails: [
      "Builds rich 3D Pixar thumbnail prompt based on project topic & characters.",
      "NEVER extracts frames from video clips (100% pure thematic illustration).",
      "Renders compact 1-2 word punchy candy title ('BLUE BUS!', 'RAIN RAIN!') that never blocks art.",
      "Saves thumbnail_prompt.txt for 1-click external copy to Midjourney / Leonardo.",
      "Generates YouTube viral title, tags, description, and preschool hashtags.",
    ],
    inputs: ["Project Topic & Character Bible", "Clean Title", "Channel Badges"],
    outputs: ["thumbnail.jpg (1280x720)", "thumbnail_prompt.txt", "YouTube SEO Package"],
    status: currentStage >= 6 ? "completed" : "ready",
    metrics: [
      { label: "Cover CTR", value: "High-CTR 3D" },
      { label: "Title Size", value: "Compact 48px" },
    ],
    actionLink: { label: "SEO & Thumbnail", href: "/studio" },
  };

  const DISTRIBUTION_NODE: EngineNodeData = {
    id: "output_distribution",
    category: "output",
    title: "Final QC Guard & YouTube Release",
    subtitle: "Broadcast Ready Distribution",
    icon: CheckCircle2,
    iconBg: "bg-emerald-600",
    iconColor: "text-white",
    aiEngine: "Quality Control & YouTube Data API v3",
    aiBadge: "Broadcast Ready",
    modelSlug: "QC Audio/Video Auditor",
    endpoint: "http://127.0.0.1:5678 (n8n) / YouTube API",
    role: "Performs final quality checks on audio loudness and frame drops, enabling 1-click export.",
    aiActionDetails: [
      "Verifies broadcast audio LUFS compliance and video/audio synchronization.",
      "Packages final.mp4, thumbnail.jpg, subtitles.srt, and SEO tags.",
      "Provides direct YouTube Creator Studio upload in Private Review Mode.",
    ],
    inputs: ["final.mp4", "thumbnail.jpg", "SEO Metadata Package"],
    outputs: ["Broadcast Master Package", "YouTube Release Payload", "QC Pass Certificate"],
    status: currentStage >= 6 ? "completed" : "standby",
    metrics: [
      { label: "QC Status", value: "PASSED 100%" },
      { label: "Distribution", value: "YouTube Ready" },
    ],
    actionLink: { label: "View Assets", href: "/assets" },
  };

  const ALL_NODES = [
    ...INPUT_NODES,
    ...CORE_NODES,
    CONDITION_NODE,
    ...BRANCH_NODES,
    COMPOSITOR_NODE,
    THUMBNAIL_NODE,
    DISTRIBUTION_NODE,
  ];

  const selectedNode =
    ALL_NODES.find((n) => n.id === selectedNodeId) || CORE_NODES[0];

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    setCursorPos({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  };

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      className="relative w-full bg-[#FAFAFC] border border-[#E5E5EA] rounded-3xl p-6 sm:p-10 shadow-xs overflow-hidden select-none"
    >
      {/* Background Engineering Blueprint Dot Grid */}
      <div
        className="absolute inset-0 pointer-events-none opacity-40"
        style={{
          backgroundImage: "radial-gradient(#CBD5E1 1px, transparent 1px)",
          backgroundSize: "20px 20px",
        }}
      />

      {/* SVG Circuit Connector Layer with Live Pulsing Energy Flow */}
      <style jsx global>{`
        @keyframes flowPulse {
          0% {
            stroke-dashoffset: 64;
          }
          100% {
            stroke-dashoffset: 0;
          }
        }
        @keyframes ringBreathe {
          0%,
          100% {
            transform: scale(1);
            opacity: 0.7;
          }
          50% {
            transform: scale(1.2);
            opacity: 1;
          }
        }
        .circuit-line-active {
          stroke-dasharray: 8 6;
          animation: flowPulse 1.2s linear infinite;
        }
        .circuit-line-idle {
          stroke-dasharray: 4 4;
        }
      `}</style>

      {/* Engine Telemetry & Header Controls */}
      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 mb-8 border-b border-[#E5E5EA]">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-[#FF6B00] via-[#FF8533] to-[#FFA366] flex items-center justify-center text-white shadow-md shadow-orange-500/20">
            <Activity className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base sm:text-lg font-extrabold text-[#1D1D1F] tracking-tight">
                Live AI Engine Architecture & Pipeline Flow
              </h2>
              <span className="text-[10px] font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1.5 shadow-xs">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
                ENGINE RUNNING
              </span>
            </div>
            <p className="text-xs text-[#6E6E73] mt-0.5">
              Production:{" "}
              <strong className="text-[#1D1D1F]">
                &ldquo;{activeProject?.title || "Bella the Blue Bus & The Fun Ride"}&rdquo;
              </strong>{" "}
              • Stage 0{currentStage}/06 Active • Hover any node for AI details
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setIsSimulating(!isSimulating)}
            className={`inline-flex items-center gap-1.5 text-xs font-bold px-3.5 py-2 rounded-xl border transition-all cursor-pointer shadow-xs ${
              isSimulating
                ? "bg-purple-50 text-purple-700 border-purple-300 ring-2 ring-purple-400/20"
                : "bg-white hover:bg-orange-50 text-[#1D1D1F] border-[#E5E5EA]"
            }`}
          >
            {isSimulating ? (
              <>
                <Pause className="w-3.5 h-3.5 text-purple-600" />
                <span>Simulating (Stage {simulatedStage})</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 text-[#FF6B00]" />
                <span>Simulate Flow</span>
              </>
            )}
          </button>

          <button
            onClick={loadData}
            disabled={refreshing}
            className="inline-flex items-center gap-1.5 bg-white hover:bg-[#F5F5F7] text-[#1D1D1F] border border-[#E5E5EA] text-xs font-semibold px-3.5 py-2 rounded-xl transition-all cursor-pointer shadow-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin text-[#FF6B00]" : ""}`} />
            <span>Ping Engine</span>
          </button>
        </div>
      </div>

      {/* ============================================================== */}
      {/* THE FLOWCHART / SCHEMATIC CANVAS (Matching Reference Screenshot) */}
      {/* ============================================================== */}
      <div className="relative z-10 max-w-2xl mx-auto flex flex-col items-center space-y-4">
        {/* Tier 1: Input Seeds (Converging from Top) */}
        <div className="w-full flex flex-col sm:flex-row items-center justify-between gap-3">
          {INPUT_NODES.map((node) => (
            <FlowNodeCard
              key={node.id}
              node={node}
              isSelected={selectedNodeId === node.id}
              onClick={() => setSelectedNodeId(node.id)}
              onHoverStart={() => setHoveredNode(node)}
              onHoverEnd={() => setHoveredNode(null)}
              compact={compact}
            />
          ))}
        </div>

        {/* Converging Dotted Cables into Central Pulse Junction */}
        <div className="w-full flex flex-col items-center relative py-1">
          <svg className="w-full h-12 overflow-visible" xmlns="http://www.w3.org/2000/svg">
            {/* Left to center conduit */}
            <path
              d="M 120 0 V 16 Q 120 28, 200 32 H 300 V 48"
              fill="none"
              stroke="#CBD5E1"
              strokeWidth="2"
              className="circuit-line-active"
            />
            {/* Center vertical conduit */}
            <path
              d="M 330 0 V 48"
              fill="none"
              stroke="#CBD5E1"
              strokeWidth="2"
              className="circuit-line-active"
            />
            {/* Right to center conduit */}
            <path
              d="M 540 0 V 16 Q 540 28, 460 32 H 360 V 48"
              fill="none"
              stroke="#CBD5E1"
              strokeWidth="2"
              className="circuit-line-active"
            />
          </svg>

          {/* Glowing Purple/Pink Junction Ring (From User Reference Image) */}
          <JunctionPulseRing label="Context Convergence" />
        </div>

        {/* Tier 2: Core Step 1 - Storyboard & Lyrics Synthesizer */}
        <div className="w-full max-w-md">
          <FlowNodeCard
            node={CORE_NODES[0]}
            isCurrent={currentStage === 1}
            isSelected={selectedNodeId === CORE_NODES[0].id}
            onClick={() => setSelectedNodeId(CORE_NODES[0].id)}
            onHoverStart={() => setHoveredNode(CORE_NODES[0])}
            onHoverEnd={() => setHoveredNode(null)}
            compact={compact}
          />
        </div>

        {/* Conduit to Step 2 */}
        <ConnectorPipe />

        {/* Tier 2: Core Step 2 - 3D Character Studio */}
        <div className="w-full max-w-md">
          <FlowNodeCard
            node={CORE_NODES[1]}
            isCurrent={currentStage === 2}
            isSelected={selectedNodeId === CORE_NODES[1].id}
            onClick={() => setSelectedNodeId(CORE_NODES[1].id)}
            onHoverStart={() => setHoveredNode(CORE_NODES[1])}
            onHoverEnd={() => setHoveredNode(null)}
            compact={compact}
          />
        </div>

        {/* Conduit to Step 3 */}
        <ConnectorPipe />

        {/* Tier 2: Core Step 3 - Neural Audio & Karaoke Sync */}
        <div className="w-full max-w-md">
          <FlowNodeCard
            node={CORE_NODES[2]}
            isCurrent={currentStage === 3}
            isSelected={selectedNodeId === CORE_NODES[2].id}
            onClick={() => setSelectedNodeId(CORE_NODES[2].id)}
            onHoverStart={() => setHoveredNode(CORE_NODES[2])}
            onHoverEnd={() => setHoveredNode(null)}
            compact={compact}
          />
        </div>

        {/* Glowing Large Pulsing Ring (Stage Gate from User Image) */}
        <div className="py-2 flex flex-col items-center">
          <ConnectorPipe length="short" />
          <JunctionPulseRing label="Audio-Visual Sync Gate" color="purple" />
          <ConnectorPipe length="short" />
        </div>

        {/* Tier 3: Condition Routing Node (Matching "Condition" in user screenshot) */}
        <div className="w-full max-w-md">
          <FlowNodeCard
            node={CONDITION_NODE}
            isCurrent={currentStage === 4}
            isSelected={selectedNodeId === CONDITION_NODE.id}
            onClick={() => setSelectedNodeId(CONDITION_NODE.id)}
            onHoverStart={() => setHoveredNode(CONDITION_NODE)}
            onHoverEnd={() => setHoveredNode(null)}
            compact={compact}
          />
        </div>

        {/* Splitting Branches (From User Reference Image) */}
        <div className="w-full flex flex-col items-center relative py-1">
          <svg className="w-full h-12 overflow-visible" xmlns="http://www.w3.org/2000/svg">
            {/* Split from center to Left (Wan AI) */}
            <path
              d="M 330 0 V 16 Q 330 28, 220 32 H 180 V 48"
              fill="none"
              stroke="#CBD5E1"
              strokeWidth="2"
              className="circuit-line-active"
            />
            {/* Split from center to Right (Creator Upload) */}
            <path
              d="M 330 0 V 16 Q 330 28, 440 32 H 480 V 48"
              fill="none"
              stroke="#CBD5E1"
              strokeWidth="2"
              className="circuit-line-active"
            />
          </svg>
        </div>

        {/* Tier 4: Parallel Branches (Wan AI vs Creator Uploads) */}
        <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FlowNodeCard
            node={BRANCH_NODES[0]}
            isCurrent={currentStage === 4}
            isSelected={selectedNodeId === BRANCH_NODES[0].id}
            onClick={() => setSelectedNodeId(BRANCH_NODES[0].id)}
            onHoverStart={() => setHoveredNode(BRANCH_NODES[0])}
            onHoverEnd={() => setHoveredNode(null)}
            compact={compact}
          />
          <FlowNodeCard
            node={BRANCH_NODES[1]}
            isCurrent={currentStage === 4}
            isSelected={selectedNodeId === BRANCH_NODES[1].id}
            onClick={() => setSelectedNodeId(BRANCH_NODES[1].id)}
            onHoverStart={() => setHoveredNode(BRANCH_NODES[1])}
            onHoverEnd={() => setHoveredNode(null)}
            compact={compact}
          />
        </div>

        {/* Re-convergence into Master Compositor */}
        <div className="w-full flex flex-col items-center relative py-1">
          <svg className="w-full h-12 overflow-visible" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M 180 0 V 16 Q 180 28, 280 32 H 330 V 48"
              fill="none"
              stroke="#CBD5E1"
              strokeWidth="2"
              className="circuit-line-active"
            />
            <path
              d="M 480 0 V 16 Q 480 28, 380 32 H 330 V 48"
              fill="none"
              stroke="#CBD5E1"
              strokeWidth="2"
              className="circuit-line-active"
            />
          </svg>
          <JunctionPulseRing label="AV Stitch Confluence" />
        </div>

        {/* Tier 5: Step 5 - Master AV Compositor & Multiplexer */}
        <div className="w-full max-w-md">
          <FlowNodeCard
            node={COMPOSITOR_NODE}
            isCurrent={currentStage === 5}
            isSelected={selectedNodeId === COMPOSITOR_NODE.id}
            onClick={() => setSelectedNodeId(COMPOSITOR_NODE.id)}
            onHoverStart={() => setHoveredNode(COMPOSITOR_NODE)}
            onHoverEnd={() => setHoveredNode(null)}
            compact={compact}
          />
        </div>

        {/* Conduit to Step 6 */}
        <ConnectorPipe />

        {/* Tier 6: Step 6 - High-CTR 3D Thumbnail & SEO Suite */}
        <div className="w-full max-w-md">
          <FlowNodeCard
            node={THUMBNAIL_NODE}
            isCurrent={currentStage === 6}
            isSelected={selectedNodeId === THUMBNAIL_NODE.id}
            onClick={() => setSelectedNodeId(THUMBNAIL_NODE.id)}
            onHoverStart={() => setHoveredNode(THUMBNAIL_NODE)}
            onHoverEnd={() => setHoveredNode(null)}
            compact={compact}
          />
        </div>

        {/* Conduit to Output */}
        <ConnectorPipe />

        {/* Tier 7: Final Distribution & QC Studio Release */}
        <div className="w-full max-w-md">
          <FlowNodeCard
            node={DISTRIBUTION_NODE}
            isCurrent={currentStage === 6}
            isSelected={selectedNodeId === DISTRIBUTION_NODE.id}
            onClick={() => setSelectedNodeId(DISTRIBUTION_NODE.id)}
            onHoverStart={() => setHoveredNode(DISTRIBUTION_NODE)}
            onHoverEnd={() => setHoveredNode(null)}
            compact={compact}
          />
        </div>

        {/* Terminal Target Icon (Matching screenshot bottom target node) */}
        <div className="pt-2 pb-4 flex flex-col items-center">
          <div className="w-10 h-10 rounded-full border-2 border-emerald-400 bg-white flex items-center justify-center shadow-xs">
            <div className="w-4 h-4 rounded-full bg-emerald-500 animate-pulse" />
          </div>
          <span className="text-[10px] font-extrabold uppercase tracking-wider text-emerald-700 mt-1">
            BROADCAST COMPLETE
          </span>
        </div>
      </div>

      {/* ============================================================== */}
      {/* FLOATING HOVER POPUP (CURSOR-FOLLOWING / SMART ANCHORED) */}
      {/* ============================================================== */}
      {hoveredNode && (
        <div
          className="fixed z-50 pointer-events-none transition-all duration-150 transform -translate-x-1/2 -translate-y-full mb-3"
          style={{
            left: `${cursorPos.x + 80}px`,
            top: `${cursorPos.y + 110}px`,
          }}
        >
          <div className="w-80 bg-white/95 backdrop-blur-md border border-[#E5E5EA] rounded-2xl p-4 shadow-xl space-y-3 ring-1 ring-black/5 animate-in fade-in zoom-in-95">
            {/* Header */}
            <div className="flex items-center justify-between pb-2 border-b border-[#F5F5F7]">
              <div className="flex items-center gap-2">
                <div
                  className={`w-7 h-7 rounded-lg ${hoveredNode.iconBg} ${hoveredNode.iconColor} flex items-center justify-center`}
                >
                  <hoveredNode.icon className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#1D1D1F] leading-tight">
                    {hoveredNode.title}
                  </h4>
                  <span className="text-[10px] text-[#6E6E73] font-medium">
                    {hoveredNode.subtitle}
                  </span>
                </div>
              </div>
              <span className="text-[9px] font-bold px-2 py-0.5 rounded-full bg-orange-50 text-[#FF6B00] border border-orange-200">
                {hoveredNode.category.toUpperCase()}
              </span>
            </div>

            {/* AI Engine & Model Badge */}
            <div className="p-2 bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl space-y-1">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-bold text-[#1D1D1F] flex items-center gap-1">
                  <Bot className="w-3.5 h-3.5 text-[#FF6B00]" />
                  AI Engine:
                </span>
                <span className="font-mono text-[10px] text-blue-600 font-semibold truncate max-w-[130px]">
                  {hoveredNode.aiBadge}
                </span>
              </div>
              <p className="text-[10px] font-mono text-[#6E6E73] truncate">
                Model: {hoveredNode.modelSlug}
              </p>
            </div>

            {/* What AI is doing here */}
            <div className="space-y-1">
              <span className="text-[10px] font-bold text-[#6E6E73] uppercase tracking-wider block">
                What AI Does Here:
              </span>
              <ul className="text-[11px] text-[#1D1D1F] space-y-1 leading-snug">
                {hoveredNode.aiActionDetails.map((detail, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span className="text-orange-500 font-bold">•</span>
                    <span>{detail}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* I/O Contracts */}
            <div className="grid grid-cols-2 gap-2 text-[10px] pt-1 border-t border-[#F5F5F7]">
              <div>
                <span className="font-bold text-[#6E6E73] uppercase block">Input Stream:</span>
                <span className="text-[#1D1D1F] truncate block">{hoveredNode.inputs[0]}</span>
              </div>
              <div>
                <span className="font-bold text-emerald-600 uppercase block">Generates:</span>
                <span className="text-[#1D1D1F] truncate block">{hoveredNode.outputs[0]}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================== */}
      {/* DETAILED INSPECTION DOCK (PINNED WHEN USER CLICKS ANY NODE) */}
      {/* ============================================================== */}
      <div className="relative z-10 mt-10 pt-6 border-t border-[#E5E5EA] bg-white rounded-2xl p-5 border shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#F5F5F7]">
          <div className="flex items-center gap-3">
            <div
              className={`w-9 h-9 rounded-xl ${selectedNode.iconBg} ${selectedNode.iconColor} flex items-center justify-center shadow-xs`}
            >
              <selectedNode.icon className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-[#1D1D1F]">{selectedNode.title}</h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-bold">
                  {selectedNode.aiBadge}
                </span>
              </div>
              <p className="text-xs text-[#6E6E73]">{selectedNode.role}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono text-[#6E6E73] bg-[#FAFAFC] px-3 py-1 rounded-lg border border-[#E5E5EA]">
              Endpoint: {selectedNode.endpoint}
            </span>
            {selectedNode.actionLink && (
              <Link
                href={selectedNode.actionLink.href}
                className="inline-flex items-center gap-1 text-xs font-bold text-white bg-[#FF6B00] hover:bg-[#EA580C] px-3 py-1.5 rounded-lg shadow-xs transition-all"
              >
                <span>{selectedNode.actionLink.label}</span>
                <ArrowRight className="w-3 h-3" />
              </Link>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          {/* Column 1: AI Actions */}
          <div className="p-3 bg-[#FAFAFC] rounded-xl border border-[#E5E5EA] space-y-1.5">
            <span className="text-[10px] font-bold text-[#6E6E73] uppercase tracking-wider block">
              🤖 Artificial Intelligence Pipeline
            </span>
            <ul className="space-y-1 text-[#1D1D1F] text-[11px]">
              {selectedNode.aiActionDetails.map((action, i) => (
                <li key={i} className="flex items-start gap-1.5">
                  <span className="text-[#FF6B00]">✓</span>
                  <span>{action}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Column 2: Inbound Inputs */}
          <div className="p-3 bg-[#FAFAFC] rounded-xl border border-[#E5E5EA] space-y-1.5">
            <span className="text-[10px] font-bold text-orange-600 uppercase tracking-wider block">
              📥 Inbound Stream Inputs
            </span>
            <ul className="space-y-1 text-[#6E6E73] text-[11px]">
              {selectedNode.inputs.map((inp, i) => (
                <li key={i} className="truncate">• {inp}</li>
              ))}
            </ul>
          </div>

          {/* Column 3: Outbound Artifacts */}
          <div className="p-3 bg-[#FAFAFC] rounded-xl border border-[#E5E5EA] space-y-1.5">
            <span className="text-[10px] font-bold text-emerald-600 uppercase tracking-wider block">
              📤 Outbound Produced Artifacts
            </span>
            <ul className="space-y-1 text-[#6E6E73] text-[11px]">
              {selectedNode.outputs.map((out, i) => (
                <li key={i} className="truncate">• {out}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

// Subcomponent: Individual Node Card (Styled exactly like the User's Screenshot Pill Nodes)
function FlowNodeCard({
  node,
  isCurrent = false,
  isSelected = false,
  onClick,
  onHoverStart,
  onHoverEnd,
  compact = false,
}: {
  node: EngineNodeData;
  isCurrent?: boolean;
  isSelected?: boolean;
  onClick: () => void;
  onHoverStart: () => void;
  onHoverEnd: () => void;
  compact?: boolean;
}) {
  const Icon = node.icon;

  return (
    <div
      onClick={onClick}
      onMouseEnter={onHoverStart}
      onMouseLeave={onHoverEnd}
      className={`group relative flex items-center gap-3 p-3.5 sm:p-4 rounded-2xl border transition-all cursor-pointer bg-white shadow-xs ${
        isCurrent
          ? "border-orange-500 ring-4 ring-orange-500/20 shadow-md shadow-orange-500/10 scale-[1.02]"
          : isSelected
          ? "border-blue-500 ring-2 ring-blue-500/20 shadow-xs"
          : "border-[#E5E5EA] hover:border-[#D1D1D6] hover:shadow-md"
      }`}
    >
      {/* Current Active Step Badge */}
      {isCurrent && (
        <div className="absolute -top-2.5 right-4 bg-gradient-to-r from-[#FF6B00] to-[#EA580C] text-white text-[9px] font-extrabold uppercase px-2 py-0.5 rounded-full shadow-xs flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-white animate-ping" />
          <span>ACTIVE ENGINE STAGE</span>
        </div>
      )}

      {/* Circular Dark Icon Badge (From Screenshot) */}
      <div
        className={`w-9 h-9 rounded-full ${node.iconBg} ${node.iconColor} flex items-center justify-center shrink-0 shadow-xs group-hover:scale-105 transition-transform`}
      >
        <Icon className="w-4 h-4" />
      </div>

      {/* Title & Tagline */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5">
          {node.stepNumber && (
            <span className="text-[10px] font-mono font-extrabold text-[#FF6B00]">
              0{node.stepNumber}.
            </span>
          )}
          <h3 className="text-xs font-bold text-[#1D1D1F] truncate group-hover:text-[#FF6B00] transition-colors">
            {node.title}
          </h3>
        </div>
        <p className="text-[10px] text-[#6E6E73] truncate font-medium mt-0.5">
          {node.subtitle}
        </p>
      </div>

      {/* Model Pill */}
      <div className="hidden sm:flex items-center gap-1 shrink-0">
        <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-[#F5F5F7] text-[#6E6E73] border border-[#E5E5EA] group-hover:border-orange-200 group-hover:text-orange-600 transition-colors">
          {node.aiBadge}
        </span>
      </div>
    </div>
  );
}

// Subcomponent: Glowing Junction Ring (The Purple/Pink Breathing Ring in Screenshot)
function JunctionPulseRing({
  label,
  color = "pink",
}: {
  label: string;
  color?: "pink" | "purple";
}) {
  return (
    <div className="relative flex items-center justify-center my-1 group">
      {/* Outer breathing aura ring */}
      <div className="w-8 h-8 rounded-full bg-pink-500/20 animate-ping absolute" />
      <div className="w-7 h-7 rounded-full border-2 border-pink-400 bg-pink-50 flex items-center justify-center shadow-xs">
        <div className="w-2.5 h-2.5 rounded-full bg-pink-500" />
      </div>
    </div>
  );
}

// Subcomponent: Vertical Connector Conduit Pipe
function ConnectorPipe({ length = "normal" }: { length?: "normal" | "short" }) {
  const h = length === "short" ? "h-4" : "h-7";
  return (
    <div className={`w-0.5 ${h} bg-slate-300 relative my-0.5 flex flex-col items-center justify-center`}>
      <div className="w-1.5 h-1.5 rounded-full bg-slate-400" />
    </div>
  );
}
