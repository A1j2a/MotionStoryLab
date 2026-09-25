"use client";

import { useEffect } from "react";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";
import Link from "next/link";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Dashboard caught client error:", error);
  }, [error]);

  return (
    <div className="flex-1 flex items-center justify-center p-8 min-h-[60vh]">
      <div className="bg-white border border-[#E5E5EA] rounded-3xl p-8 max-w-md w-full text-center shadow-lg space-y-5">
        <div className="w-14 h-14 bg-amber-50 text-amber-600 border border-amber-200 rounded-2xl flex items-center justify-center mx-auto shadow-xs">
          <AlertTriangle className="w-7 h-7" />
        </div>

        <div className="space-y-2">
          <h2 className="text-xl font-bold text-[#1D1D1F]">
            Something unexpected occurred
          </h2>
          <p className="text-xs text-[#6E6E73] leading-relaxed">
            {error?.message || "An issue occurred while updating the project state. You can safely retry or return to dashboard."}
          </p>
        </div>

        <div className="flex items-center justify-center gap-3 pt-2">
          <button
            onClick={() => reset()}
            className="inline-flex items-center gap-2 bg-[#FF6B00] hover:bg-[#EA580C] text-white text-xs font-bold px-4 py-2.5 rounded-xl transition-all shadow-xs cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Try Again</span>
          </button>

          <Link
            href="/"
            className="inline-flex items-center gap-2 bg-[#F5F5F7] hover:bg-[#E5E5EA] text-[#1D1D1F] text-xs font-semibold px-4 py-2.5 rounded-xl transition-all cursor-pointer border border-[#E5E5EA]"
          >
            <Home className="w-3.5 h-3.5" />
            <span>Dashboard</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
