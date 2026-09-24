"use client";

import {
  FileText,
  Users2,
  Music,
  Clapperboard,
  Film,
  CheckCircle2,
  Loader2,
  Sparkles,
} from "lucide-react";

interface PipelineStepperProps {
  status: string;
  step: string;
  progress: number;
}

export function PipelineStepper({ status, step, progress }: PipelineStepperProps) {
  const steps = [
    {
      id: "planning",
      title: "1. AI Story & Lyrics",
      desc: "Nursery rhyme lyrics & shot list",
      icon: FileText,
      minProgress: 10,
    },
    {
      id: "characters",
      title: "2. Character Bible & World",
      desc: "Consistent storybook assets & styling",
      icon: Users2,
      minProgress: 25,
    },
    {
      id: "audio",
      title: "3. Music & Vocals",
      desc: "Chime melody, narration & SRT",
      icon: Music,
      minProgress: 40,
    },
    {
      id: "rendering",
      title: "4. Illustrated Story Engine",
      desc: "Preschool Stylized kinetic animation",
      icon: Clapperboard,
      minProgress: 75,
    },
    {
      id: "compositing",
      title: "5. Multi-track Stitch",
      desc: "FFmpeg audio & video muxing",
      icon: Film,
      minProgress: 90,
    },
    {
      id: "approval",
      title: "6. SEO & YouTube Ready",
      desc: "1080p preview & metadata package",
      icon: CheckCircle2,
      minProgress: 100,
    },
  ];

  const isCompleted = progress >= 100 || status === "COMPLETED" || status === "READY" || status === "APPROVED";

  // Calculate current active step index
  let activeIndex = 0;
  for (let i = 0; i < steps.length; i++) {
    if (progress >= steps[i].minProgress) {
      activeIndex = i + 1;
    }
  }
  if (isCompleted) activeIndex = 5;

  return (
    <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 shadow-xs space-y-6">
      {/* Top Header & Master Progress */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#FF6B00] animate-pulse" />
            <h3 className="text-sm font-bold text-[#1D1D1F] tracking-tight uppercase">
              Automated Video Pipeline Sequence
            </h3>
          </div>
          <p className="text-xs text-[#6E6E73] mt-0.5">
            Real-time stage tracking across local Apple Silicon M4 engine
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <span className="text-[11px] font-bold text-[#EA580C] uppercase tracking-wider block">
              {step || status || "IN_PROGRESS"}
            </span>
            <span className="text-xs text-[#86868B]">
              {isCompleted ? "All Stages Completed" : "Sequential Processing"}
            </span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-[#FFF7ED] border border-[#FED7AA] flex items-center justify-center font-bold text-[#EA580C] text-sm shadow-xs font-mono">
            {progress}%
          </div>
        </div>
      </div>

      {/* Sleek Master Progress Bar */}
      <div className="w-full bg-[#F5F5F7] h-2 rounded-full overflow-hidden p-0.5 border border-[#E5E5EA]">
        <div
          className="h-full rounded-full bg-gradient-to-r from-[#FF6B00] via-[#FF8533] to-[#EA580C] transition-all duration-500 shadow-xs"
          style={{ width: `${Math.max(3, Math.min(100, progress))}%` }}
        />
      </div>

      {/* 6-Stage Stepper Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {steps.map((st, idx) => {
          const Icon = st.icon;
          const isStepDone = isCompleted || progress >= st.minProgress;
          const isCurrent = !isCompleted && idx === Math.min(activeIndex, steps.length - 1);

          return (
            <div
              key={st.id}
              className={`p-3 rounded-xl border transition-all flex flex-col justify-between ${
                isStepDone
                  ? "bg-[#F0FDF4] border-[#BBF7D0]"
                  : isCurrent
                  ? "bg-[#FFF7ED] border-[#FED7AA] shadow-sm ring-2 ring-[#FF6B00]/20"
                  : "bg-[#FAFAFC] border-[#E5E5EA] opacity-60"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div
                  className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                    isStepDone
                      ? "bg-emerald-600 text-white"
                      : isCurrent
                      ? "bg-[#FF6B00] text-white"
                      : "bg-[#E5E5EA] text-[#86868B]"
                  }`}
                >
                  {isCurrent ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Icon className="w-3.5 h-3.5" />
                  )}
                </div>
                <span
                  className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                    isStepDone
                      ? "bg-emerald-100 text-emerald-800"
                      : isCurrent
                      ? "bg-[#FFEDD5] text-[#C2410C]"
                      : "bg-[#E5E5EA] text-[#86868B]"
                  }`}
                >
                  {isStepDone ? "DONE" : isCurrent ? "ACTIVE" : "QUEUED"}
                </span>
              </div>

              <div>
                <h4 className="text-xs font-bold text-[#1D1D1F] leading-tight">
                  {st.title}
                </h4>
                <p className="text-[10px] text-[#6E6E73] mt-1 line-clamp-2 leading-tight">
                  {st.desc}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
