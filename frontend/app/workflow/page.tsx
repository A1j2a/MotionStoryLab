"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { InteractiveEngineFlow } from "@/components/InteractiveEngineFlow";
import Link from "next/link";
import {
  Sparkles,
  Bot,
  Film,
  Music,
  ArrowRight,
  Cpu,
  Tv,
  Layers,
  CheckCircle2,
  GitBranch,
} from "lucide-react";

export default function WorkflowEnginePage() {
  return (
    <>
      <Header
        title="AI Production Engine Workflow & Schematic"
        subtitle="Live interactive node architecture: discover where each AI operates with animated signal flows and cursor popups"
      />

      <main className="p-4 sm:p-8 space-y-8 flex-1 max-w-7xl mx-auto w-full">
        {/* Main Interactive Engine Flowchart */}
        <InteractiveEngineFlow />

        {/* AI Factory Architecture Breakdown Card */}
        <div className="bg-white border border-[#E5E5EA] rounded-3xl p-6 sm:p-8 shadow-xs space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#E5E5EA]">
            <div>
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-[#FF6B00]" />
                <h3 className="text-base font-bold text-[#1D1D1F]">
                  Studio Artificial Intelligence Directory & Responsibilities
                </h3>
              </div>
              <p className="text-xs text-[#6E6E73] mt-1">
                Summary of the deep learning engines, neural models, and audio DSP pipelines powering MotionStoryLab.
              </p>
            </div>
            <Link
              href="/settings"
              className="inline-flex items-center gap-1.5 text-xs font-bold text-[#FF6B00] hover:text-[#EA580C] bg-orange-50 px-3.5 py-1.5 rounded-xl border border-orange-200 transition-all self-start sm:self-auto"
            >
              <span>Configure AI Models</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Card 1: OpenRouter & DeepSeek */}
            <div className="p-4 bg-[#FAFAFC] border border-[#E5E5EA] rounded-2xl space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-orange-100 text-orange-600 flex items-center justify-center font-bold">
                  <Bot className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#1D1D1F]">OpenRouter & Ollama</h4>
                  <span className="text-[10px] text-[#6E6E73] font-mono">deepseek-r1 / llama3.2</span>
                </div>
              </div>
              <p className="text-[11px] text-[#6E6E73] leading-relaxed">
                Researches viral toddler hooks, constructs rhyming lyrics with AABB meter, and plans 18 distinct animated scene visual choreographies.
              </p>
              <div className="pt-2 text-[10px] font-mono text-orange-600 flex items-center gap-1 font-semibold">
                <span>Output:</span>
                <span className="bg-white px-2 py-0.5 rounded border border-orange-200">lyrics.json • scenes.json</span>
              </div>
            </div>

            {/* Card 2: Wan 2.1 Video */}
            <div className="p-4 bg-[#FAFAFC] border border-[#E5E5EA] rounded-2xl space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center font-bold">
                  <Film className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#1D1D1F]">Wan 2.1 Video Engine</h4>
                  <span className="text-[10px] text-[#6E6E73] font-mono">fal-ai/wan-flf2v</span>
                </div>
              </div>
              <p className="text-[11px] text-[#6E6E73] leading-relaxed">
                Generates 720p 24fps First-Frame to Last-Frame 3D videos with camera motions, negative human filters, and smooth character gestures.
              </p>
              <div className="pt-2 text-[10px] font-mono text-purple-600 flex items-center gap-1 font-semibold">
                <span>Output:</span>
                <span className="bg-white px-2 py-0.5 rounded border border-purple-200">scene_001.mp4 - 018.mp4</span>
              </div>
            </div>

            {/* Card 3: Suno & Kokoro */}
            <div className="p-4 bg-[#FAFAFC] border border-[#E5E5EA] rounded-2xl space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center font-bold">
                  <Music className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#1D1D1F]">Suno AI & Kokoro</h4>
                  <span className="text-[10px] text-[#6E6E73] font-mono">Suno v3.5 / Kokoro TTS</span>
                </div>
              </div>
              <p className="text-[11px] text-[#6E6E73] leading-relaxed">
                Synthesizes 120-128 BPM bounce toddler sing-along audio with chime orchestration and generates millisecond-accurate karaoke SRT subtitles.
              </p>
              <div className="pt-2 text-[10px] font-mono text-emerald-600 flex items-center gap-1 font-semibold">
                <span>Output:</span>
                <span className="bg-white px-2 py-0.5 rounded border border-emerald-200">master_soundtrack.wav • subtitles.srt</span>
              </div>
            </div>

            {/* Card 4: FFmpeg Compositor */}
            <div className="p-4 bg-[#FAFAFC] border border-[#E5E5EA] rounded-2xl space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-pink-100 text-pink-600 flex items-center justify-center font-bold">
                  <Cpu className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#1D1D1F]">FFmpeg 7.1 Compositor</h4>
                  <span className="text-[10px] text-[#6E6E73] font-mono">Multi-Track DSP Engine</span>
                </div>
              </div>
              <p className="text-[11px] text-[#6E6E73] leading-relaxed">
                Multiplexes clip sound + song audio simultaneously, burns karaoke subtitles at screen bottom, and overlays logo with dynamic bottom spacing.
              </p>
              <div className="pt-2 text-[10px] font-mono text-pink-600 flex items-center gap-1 font-semibold">
                <span>Output:</span>
                <span className="bg-white px-2 py-0.5 rounded border border-pink-200">final.mp4 (Broadcast 720p/1080p)</span>
              </div>
            </div>

            {/* Card 5: High-CTR 3D Thumbnail */}
            <div className="p-4 bg-[#FAFAFC] border border-[#E5E5EA] rounded-2xl space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center font-bold">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#1D1D1F]">High-CTR Thumbnail AI</h4>
                  <span className="text-[10px] text-[#6E6E73] font-mono">Pixar Prompt / Flux</span>
                </div>
              </div>
              <p className="text-[11px] text-[#6E6E73] leading-relaxed">
                Generates 3D Pixar artwork prompt based on topic/characters (never from video frame), overlays compact 1-2 word candy bubble title ('BLUE BUS!').
              </p>
              <div className="pt-2 text-[10px] font-mono text-amber-600 flex items-center gap-1 font-semibold">
                <span>Output:</span>
                <span className="bg-white px-2 py-0.5 rounded border border-amber-200">thumbnail.jpg • thumbnail_prompt.txt</span>
              </div>
            </div>

            {/* Card 6: YouTube QC Auditor */}
            <div className="p-4 bg-[#FAFAFC] border border-[#E5E5EA] rounded-2xl space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center font-bold">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#1D1D1F]">Quality Control & Release</h4>
                  <span className="text-[10px] text-[#6E6E73] font-mono">Automated Auditor / YouTube API</span>
                </div>
              </div>
              <p className="text-[11px] text-[#6E6E73] leading-relaxed">
                Verifies audio LUFS broadcast standards, frame cadence, zero black frames, and publishes to YouTube Studio in private creator review mode.
              </p>
              <div className="pt-2 text-[10px] font-mono text-blue-600 flex items-center gap-1 font-semibold">
                <span>Output:</span>
                <span className="bg-white px-2 py-0.5 rounded border border-blue-200">QC Pass Certificate • YouTube Payload</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
