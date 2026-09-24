import { JobStatus } from "@/lib/types";

interface JobProgressBarProps {
  status: JobStatus | string;
  step: string;
  progress: number;
  error?: string | null;
}

export function JobProgressBar({ status, step, progress, error }: JobProgressBarProps) {
  const isFailed = status === "FAILED";
  const isCompleted = status === "COMPLETED";

  return (
    <div className="space-y-1.5 w-full">
      <div className="flex justify-between items-center text-xs">
        <span className="font-semibold text-slate-300 uppercase tracking-wider text-[10px]">
          {step || status}
        </span>
        <span className="text-slate-400 font-mono">{progress}%</span>
      </div>

      <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden p-0.5">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            isFailed
              ? "bg-rose-500"
              : isCompleted
              ? "bg-emerald-400"
              : "bg-gradient-to-r from-indigo-500 to-purple-500"
          }`}
          style={{ width: `${Math.max(3, Math.min(100, progress))}%` }}
        />
      </div>

      {error && (
        <p className="text-[11px] text-rose-400 bg-rose-950/40 border border-rose-800/60 p-2 rounded-lg mt-2">
          {error}
        </p>
      )}
    </div>
  );
}
