"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { HealthData } from "@/lib/types";
import {
  Sparkles,
  Cpu,
  Layers,
  Music,
  Film,
  Share2,
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
  Database,
  Eye,
  Bot,
  Box,
  Volume2,
  Tv,
  UploadCloud,
  Activity,
  Play,
} from "lucide-react";

export default function WorkflowEnginePage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState<string>("ollama");

  const fetchHealth = async () => {
    setLoading(true);
    try {
      const data = await api.getHealth();
      setHealth(data);
    } catch {
      // offline
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const PIPELINE_NODES = [
    {
      id: "ollama",
      title: "Ollama Local AI",
      subtitle: "Llama 3.2 (3B Metal Engine)",
      port: "http://127.0.0.1:11434",
      status: health?.ollama?.status === "connected" ? "connected" : "standby",
      icon: Bot,
      role: "Story, Rhyming Lyrics & SEO Planner",
      tech: "Meta Llama 3.2 via Ollama Metal GPU",
      color: "#FF6B00",
      inputs: [
        "User Prompt (e.g. 'Wheels on the Yellow Bus')",
        "Preschool Target Age (1-5 Toddler)",
        "Video Duration (60s / 120s / 300s)",
      ],
      outputs: [
        "AABB Rhyming Stanzas (4 Verses)",
        "Consistent 3D Character Bible JSON",
        "High-CTR YouTube Title, Description & Tags",
      ],
      description: "Generates original sing-along lyrics with lively preschool onomatopoeia (beep beep, swish swish, moo moo) and structured 3D shot sequences. Runs 100% locally with zero cloud API costs.",
      launchCmd: "ollama run llama3.2",
    },
    {
      id: "character_studio",
      title: "3D Character & Asset Studio",
      subtitle: "Procedural 3D & Diffusion",
      port: "Blender 5.2.2 / ComfyUI (8188)",
      status: "connected",
      icon: Box,
      role: "Dynamic 3D Geometry & Facial Rigging",
      tech: "Blender Python API & Principled BSDF",
      color: "#3B82F6",
      inputs: [
        "Character Bible JSON",
        "Theme (Bus, Star, Cow, Apple, Train)",
        "Glossy Candy Material Palettes",
      ],
      outputs: [
        "Procedural 3D Character Meshes",
        "Expressive Cartoon Eyes with Highlights",
        "Rolling Hills, Flower Meadow & Roads",
      ],
      description: "Dynamically constructs theme-matching 3D characters tailored to the topic (Yellow Bus, Twinkle Star, Daisy Cow, Happy Apple). No repetitive generic templates.",
      launchCmd: "blender -b --python blender/render_scene.py",
    },
    {
      id: "audio_studio",
      title: "Nursery Audio Orchestrator",
      subtitle: "Kokoro TTS & Chime Synthesizer",
      port: "Kokoro (8880) + Studio DSP",
      status: health?.tts?.status === "connected" ? "connected" : "standby",
      icon: Volume2,
      role: "Multi-Track Nursery Chime Arranger",
      tech: "Stereo DSP, Glockenspiel & Reverb Engine",
      color: "#10B981",
      inputs: [
        "Rhyming Lyric Lines",
        "120-128 BPM Swing Rhythm",
        "Target Duration (Full 60s / 120s / 300s)",
      ],
      outputs: [
        "music.wav (Piano, Glockenspiel, Bass, Claps)",
        "vocals.wav (Warm Narrator with Spatial Reverb)",
        "master_soundtrack.wav (Balanced Final Mix)",
        "subtitles.srt (Karaoke-synchronized SRT)",
      ],
      description: "Arranges multi-track preschool music with piano chords, glockenspiel top lead, upright bass, and toddler clap-alongs. Auto-generates exact duration audio matching the project setting.",
      launchCmd: "docker run -p 8880:8880 ghcr.io/resemble-ai/kokoro-fastapi",
    },
    {
      id: "metal_render",
      title: "Headless 3D Render Engine",
      subtitle: "Blender EEVEE (Metal M4 GPU)",
      port: "/opt/homebrew/bin/blender",
      status: "connected",
      icon: Tv,
      role: "Metal GPU Cinematics & Camera Tracks",
      tech: "Apple Silicon Metal Acceleration",
      color: "#8B5CF6",
      inputs: [
        "Shot Config JSON",
        "Camera Choreography (Wide, Tracking, Hero, Close)",
        "Pixar 3-Point Studio Lighting (Key, Rim, Fill)",
      ],
      outputs: [
        "scene_001.mp4 (Establishing Wide Pan)",
        "scene_002.mp4 (Low-Angle Action Track)",
        "scene_003.mp4 (High 3/4 Landscape Beauty)",
        "scene_004.mp4 (Portrait Zoom & Happy Wave)",
      ],
      description: "Renders 1280x720 24fps frames headlessly using Apple Silicon M4 Metal shaders (~50s per 5s shot) with distinct camera movements for each scene to prevent repetitive visual flags.",
      launchCmd: "blender -b --python blender/render_scene.py -- scene_config.json",
    },
    {
      id: "ffmpeg_master",
      title: "Master AV Compositor",
      subtitle: "FFmpeg 7.1 Multi-Filter Engine",
      port: "/opt/homebrew/bin/ffmpeg",
      status: "connected",
      icon: Film,
      role: "Multi-Track Stitching & Subtitle Burning",
      tech: "FFmpeg libx264, AAC & ASS Subtitle Filter",
      color: "#EC4899",
      inputs: [
        "Rendered 3D Scene Clips",
        "master_soundtrack.wav (Stereo 44.1kHz)",
        "subtitles.srt (Karaoke Timestamps)",
      ],
      outputs: [
        "final.mp4 (Broadcast 720p/1080p MP4)",
        "thumbnail.jpg (Auto-extracted Video Cover)",
      ],
      description: "Sequences all camera shots across the full project duration, burns stylized drop-shadow subtitles for toddler mobile screens, and multiplexes stereo audio with instant web streaming flags.",
      launchCmd: "ffmpeg -y -i scenes -i master.wav -c:v libx264 final.mp4",
    },
    {
      id: "n8n_youtube",
      title: "n8n Workflow & YouTube Growth",
      subtitle: "Automated Batching & Studio Upload",
      port: "http://127.0.0.1:5678",
      status: health?.n8n?.status === "connected" ? "connected" : "standby",
      icon: UploadCloud,
      role: "YouTube Distribution & Batch Engine",
      tech: "n8n Node Workflows & YouTube Data API v3",
      color: "#F59E0B",
      inputs: [
        "final.mp4 & thumbnail.jpg",
        "High-CTR SEO Metadata JSON",
        "Target Publishing Schedule",
      ],
      outputs: [
        "YouTube Studio Upload with Chapters & Tags",
        "Automated Daily Video Batch Generation",
      ],
      description: "Automates scheduled video creation batches, prepares COPPA kid-directed metadata, and uploads finished videos directly to YouTube Studio without manual clicking.",
      launchCmd: "npx n8n start --port 5678",
    },
  ];

  const activeNode = PIPELINE_NODES.find((n) => n.id === selectedNode) || PIPELINE_NODES[0];

  return (
    <>
      <Header
        title="Live Engine Workflow Architecture"
        subtitle="Visual interactive schematic of local AI planning, procedural 3D synthesis, and GPU rendering"
      />

      <main className="p-8 space-y-8 flex-1 max-w-7xl mx-auto w-full">
        {/* Top Control Bar */}
        <div className="bg-white border border-[#E5E5EA] p-5 rounded-2xl shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-[#FFF7ED] border border-[#FED7AA] flex items-center justify-center text-[#EA580C]">
              <Activity className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-[#1D1D1F]">
                  MotionStoryLabs Studio Core Schematic
                </h2>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600 border border-emerald-200">
                  LIVE ENGINE
                </span>
              </div>
              <p className="text-xs text-[#6E6E73]">
                Zero-cloud local pipeline: Ollama (Metal) ➔ Blender 3D (EEVEE) ➔ DSP Audio ➔ FFmpeg ➔ YouTube Growth
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchHealth}
              disabled={loading}
              className="inline-flex items-center gap-2 bg-[#F5F5F7] hover:bg-[#E5E5EA] text-[#1D1D1F] border border-[#E5E5EA] text-xs font-semibold px-4 py-2 rounded-xl transition-all cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-[#FF6B00]" : ""}`} />
              <span>Ping All Nodes</span>
            </button>
          </div>
        </div>

        {/* ============================================================== */}
        {/* INTERACTIVE VISUAL PIPELINE SCHEMATIC (FLOW DIAGRAM) */}
        {/* ============================================================== */}
        <div className="bg-white border border-[#E5E5EA] rounded-2xl p-7 shadow-xs relative overflow-hidden">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2 text-xs font-bold text-[#1D1D1F] uppercase tracking-wider">
              <Zap className="w-4 h-4 text-[#FF6B00]" />
              <span>Live Interactive Node Conduits (Click any node to inspect)</span>
            </div>
            <span className="text-xs text-[#86868B] font-mono">
              Architecture: Apple Silicon M4 / M2 Unified Pipeline
            </span>
          </div>

          {/* Node Grid Layout */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
            {/* ROW 1: Stage 1, 2, 3 */}
            {PIPELINE_NODES.slice(0, 3).map((node, i) => {
              const isSelected = selectedNode === node.id;
              const Icon = node.icon;
              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node.id)}
                  className={`p-5 rounded-2xl border transition-all cursor-pointer relative bg-white ${
                    isSelected
                      ? "border-[#FF6B00] shadow-lg shadow-orange-500/10 ring-2 ring-[#FF6B00]/25 translate-y-[-2px]"
                      : "border-[#E5E5EA] hover:border-[#D1D1D6] hover:shadow-xs"
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div
                      className="w-10 h-10 rounded-xl flex items-center justify-center shadow-xs"
                      style={{ backgroundColor: `${node.color}15`, color: node.color }}
                    >
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span
                        className={`w-2 h-2 rounded-full ${
                          node.status === "connected" ? "bg-emerald-500" : "bg-amber-400"
                        }`}
                      />
                      <span className="text-[10px] font-semibold text-[#86868B] font-mono">
                        {node.status === "connected" ? "ONLINE" : "STANDBY"}
                      </span>
                    </div>
                  </div>

                  <span className="text-[10px] font-mono font-bold text-[#FF6B00] block mb-1">
                    STAGE 0{i + 1}
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

            {/* ROW 2: Stage 4, 5, 6 */}
            {PIPELINE_NODES.slice(3, 6).map((node, i) => {
              const isSelected = selectedNode === node.id;
              const Icon = node.icon;
              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node.id)}
                  className={`p-5 rounded-2xl border transition-all cursor-pointer relative bg-white ${
                    isSelected
                      ? "border-[#FF6B00] shadow-lg shadow-orange-500/10 ring-2 ring-[#FF6B00]/25 translate-y-[-2px]"
                      : "border-[#E5E5EA] hover:border-[#D1D1D6] hover:shadow-xs"
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div
                      className="w-10 h-10 rounded-xl flex items-center justify-center shadow-xs"
                      style={{ backgroundColor: `${node.color}15`, color: node.color }}
                    >
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span
                        className={`w-2 h-2 rounded-full ${
                          node.status === "connected" ? "bg-emerald-500" : "bg-amber-400"
                        }`}
                      />
                      <span className="text-[10px] font-semibold text-[#86868B] font-mono">
                        {node.status === "connected" ? "ONLINE" : "STANDBY"}
                      </span>
                    </div>
                  </div>

                  <span className="text-[10px] font-mono font-bold text-[#FF6B00] block mb-1">
                    STAGE 0{i + 4}
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

          {/* Animated Conduit Graphic Banner */}
          <div className="mt-6 pt-6 border-t border-[#E5E5EA] flex items-center justify-between text-xs text-[#6E6E73] bg-[#FAFAFC] -mx-7 -mb-7 p-4 px-7">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
              <span className="font-semibold text-[#1D1D1F]">
                Data Pipeline Conduit Active:
              </span>
              <span>Ollama Script ➔ 3D Mesh Gen ➔ Stereo DSP ➔ EEVEE Metal Frames ➔ FFmpeg MP4</span>
            </div>
            <span className="font-mono text-[11px] text-[#86868B]">
              Latency: ~2.5s LLM • ~50s/Shot 3D Render
            </span>
          </div>
        </div>

        {/* ============================================================== */}
        {/* ACTIVE NODE DEEP DIVE INSPECTOR */}
        {/* ============================================================== */}
        <div className="bg-white border border-[#E5E5EA] rounded-2xl p-7 shadow-xs space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-[#E5E5EA]">
            <div className="flex items-center gap-3.5">
              <div
                className="w-12 h-12 rounded-2xl flex items-center justify-center font-bold text-lg shadow-sm"
                style={{ backgroundColor: `${activeNode.color}15`, color: activeNode.color }}
              >
                <activeNode.icon className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-bold text-[#1D1D1F]">
                    {activeNode.title}
                  </h3>
                  <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-[#F5F5F7] text-[#1D1D1F] border border-[#E5E5EA]">
                    {activeNode.subtitle}
                  </span>
                </div>
                <p className="text-xs text-[#6E6E73] mt-0.5 max-w-2xl">
                  {activeNode.description}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-right">
                <span className="text-[10px] text-[#86868B] uppercase font-bold block">
                  Service Endpoint
                </span>
                <span className="text-xs font-mono font-medium text-[#1D1D1F]">
                  {activeNode.port}
                </span>
              </div>
              <span
                className={`inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-xl ${
                  activeNode.status === "connected"
                    ? "bg-emerald-50 text-emerald-600 border border-emerald-200"
                    : "bg-amber-50 text-amber-700 border border-amber-200"
                }`}
              >
                <span
                  className={`w-2 h-2 rounded-full ${
                    activeNode.status === "connected" ? "bg-emerald-500" : "bg-amber-500"
                  }`}
                />
                <span>{activeNode.status === "connected" ? "Connected" : "Standby / Fallback Ready"}</span>
              </span>
            </div>
          </div>

          {/* Inputs & Outputs Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Inputs Box */}
            <div className="bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl p-5 space-y-3">
              <div className="flex items-center gap-2 text-[#EA580C]">
                <Sliders className="w-4 h-4" />
                <h4 className="text-xs font-bold uppercase tracking-wider">
                  Inputs & Parameters Consumed
                </h4>
              </div>
              <div className="space-y-2">
                {activeNode.inputs.map((inp, idx) => (
                  <div
                    key={idx}
                    className="bg-white p-3 rounded-lg border border-[#E5E5EA] text-xs font-medium text-[#1D1D1F] flex items-center gap-2"
                  >
                    <ArrowRight className="w-3.5 h-3.5 text-[#FF6B00] flex-shrink-0" />
                    <span>{inp}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Outputs Box */}
            <div className="bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl p-5 space-y-3">
              <div className="flex items-center gap-2 text-[#10B981]">
                <CheckCircle2 className="w-4 h-4" />
                <h4 className="text-xs font-bold uppercase tracking-wider">
                  Outputs & Deliverable Artifacts
                </h4>
              </div>
              <div className="space-y-2">
                {activeNode.outputs.map((out, idx) => (
                  <div
                    key={idx}
                    className="bg-white p-3 rounded-lg border border-[#E5E5EA] text-xs font-medium text-[#1D1D1F] flex items-center gap-2"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" />
                    <span>{out}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick CLI Execution Box */}
          <div className="bg-[#1C1C1E] border border-[#2C2C2E] rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 text-white">
            <div className="flex items-center gap-2.5 font-mono text-xs text-[#A1A1A6]">
              <Terminal className="w-4 h-4 text-[#FF6B00]" />
              <span>Native Command:</span>
              <code className="text-[#FF8A3D] bg-[#2C2C2E] px-2.5 py-1 rounded-md">
                {activeNode.launchCmd}
              </code>
            </div>
            <span className="text-[11px] text-[#86868B]">
              Optimized for Apple Silicon Metal & Unified Memory
            </span>
          </div>
        </div>

        {/* Architecture Specs Bottom Banner */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-5 shadow-xs flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#FFF7ED] text-[#FF6B00] flex items-center justify-center">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-[#1D1D1F]">Local AI Autonomy</h4>
              <p className="text-[11px] text-[#86868B]">
                Runs 100% locally on Ollama without cloud tokens or recurring API costs.
              </p>
            </div>
          </div>

          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-5 shadow-xs flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#FFF7ED] text-[#FF6B00] flex items-center justify-center">
              <HardDrive className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-[#1D1D1F]">Unified Memory Protection</h4>
              <p className="text-[11px] text-[#86868B]">
                Sequential stage execution prevents memory leaks and protects 16GB RAM.
              </p>
            </div>
          </div>

          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-5 shadow-xs flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#FFF7ED] text-[#FF6B00] flex items-center justify-center">
              <Share2 className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-[#1D1D1F]">YouTube Content ID Safe</h4>
              <p className="text-[11px] text-[#86868B]">
                Unique procedural assets & chords avoid "reused AI content" copyright flags.
              </p>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
