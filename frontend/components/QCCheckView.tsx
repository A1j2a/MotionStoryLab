"use client";

import { QCResult } from "@/lib/types";
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Film,
  Music,
  Clapperboard,
  FileText,
  Users2,
  Subtitles,
} from "lucide-react";

interface QCCheckViewProps {
  qcResult: QCResult | null;
  onRerunQC: () => void;
  loading?: boolean;
}

export function QCCheckView({ qcResult, onRerunQC, loading }: QCCheckViewProps) {
  if (!qcResult) {
    return (
      <div className="p-6 bg-[#FAFAFC] border border-[#E5E5EA] rounded-3xl text-center space-y-3">
        <ShieldCheck className="w-8 h-8 text-[#86868B] mx-auto" />
        <p className="text-xs text-[#6E6E73]">Quality control checks have not been run yet.</p>
        <button
          onClick={onRerunQC}
          disabled={loading}
          className="inline-flex items-center gap-2 bg-[#1D1D1F] text-white text-xs font-bold px-4 py-2 rounded-xl hover:opacity-90 transition-opacity cursor-pointer"
        >
          <span>Run Quality Control Check</span>
        </button>
      </div>
    );
  }

  const items = [
    { label: "Video Integrity (MP4 1080p)", ok: qcResult.checks.video, icon: Film },
    { label: "Master Soundtrack & Vocals", ok: qcResult.checks.audio, icon: Music },
    { label: "Rendered 3D Scene Shots", ok: qcResult.checks.scenes, icon: Clapperboard },
    { label: "Approved Lyrics Consistency", ok: qcResult.checks.lyrics, icon: FileText },
    { label: "Character Bible Consistency", ok: qcResult.checks.characters, icon: Users2 },
    { label: "Synchronized SRT Subtitles", ok: qcResult.checks.subtitles, icon: Subtitles },
  ];

  return (
    <div className="bg-white border border-[#E5E5EA] rounded-3xl p-6 shadow-xs space-y-5">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-4 border-b border-[#E5E5EA]">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>Step 8 • Automated Quality Control (QC)</span>
          </div>
          <h2 className="text-lg font-bold text-[#1D1D1F]">
            Production Quality Verification Report
          </h2>
        </div>

        <div className="flex items-center gap-3">
          <span
            className={`px-3 py-1 rounded-full text-xs font-extrabold uppercase tracking-wider ${
              qcResult.status === "passed"
                ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                : qcResult.status === "warning"
                ? "bg-amber-100 text-amber-800 border border-amber-300"
                : "bg-rose-100 text-rose-800 border border-rose-300"
            }`}
          >
            QC Status: {qcResult.status}
          </span>
          <button
            onClick={onRerunQC}
            disabled={loading}
            className="text-xs font-bold text-[#FF6B00] hover:underline cursor-pointer"
          >
            Re-run QC
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {items.map((it, idx) => {
          const Icon = it.icon;
          return (
            <div
              key={idx}
              className={`p-3.5 rounded-2xl border flex items-center justify-between gap-3 ${
                it.ok ? "bg-emerald-50/20 border-emerald-200" : "bg-rose-50/20 border-rose-200"
              }`}
            >
              <div className="flex items-center gap-2.5">
                <div
                  className={`w-8 h-8 rounded-xl flex items-center justify-center ${
                    it.ok ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>
                <span className="text-xs font-bold text-[#1D1D1F]">{it.label}</span>
              </div>
              {it.ok ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              ) : (
                <XCircle className="w-4 h-4 text-rose-600 shrink-0" />
              )}
            </div>
          );
        })}
      </div>

      {qcResult.details && qcResult.details.length > 0 && (
        <div className="p-4 bg-[#FAFAFC] rounded-2xl border border-[#EDEDF0] space-y-1.5 text-xs text-[#6E6E73]">
          <span className="font-bold text-[#1D1D1F]">Verification Log:</span>
          <ul className="list-disc list-inside space-y-1 text-[11px]">
            {qcResult.details.map((d, idx) => (
              <li key={idx}>{d}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
