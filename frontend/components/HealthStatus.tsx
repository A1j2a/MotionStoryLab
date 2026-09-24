"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { HealthData } from "@/lib/types";
import { RefreshCw } from "lucide-react";

export function HealthStatus() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(false);

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
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const services = [
    { name: "FastAPI Engine", status: health?.backend?.status || "offline" },
    { name: "Ollama AI", status: health?.ollama?.status || "offline" },
    { name: "Kokoro TTS", status: health?.tts?.status || "offline" },
    { name: "FFmpeg Media", status: health?.ffmpeg?.status || "offline" },
  ];

  return (
    <div className="bg-white border border-[#E5E5EA] rounded-xl p-3 text-xs shadow-xs">
      <div className="flex items-center justify-between mb-2">
        <span className="font-semibold text-[#6E6E73] uppercase tracking-wider text-[9px]">
          M4 Studio Engine
        </span>
        <button
          onClick={fetchHealth}
          disabled={loading}
          className="text-[#86868B] hover:text-[#1D1D1F] transition-colors cursor-pointer"
          title="Refresh health"
        >
          <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>
      <div className="grid grid-cols-2 gap-1.5">
        {services.map((s) => {
          const isOnline = s.status === "connected";
          return (
            <div
              key={s.name}
              className="flex items-center justify-between bg-[#F5F5F7] px-2 py-1.5 rounded-lg border border-[#E5E5EA]/60"
            >
              <span className="text-[10px] text-[#1D1D1F] font-medium truncate max-w-[70px]">
                {s.name}
              </span>
              <span className="flex items-center gap-1">
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    isOnline ? "bg-emerald-500 animate-pulse" : "bg-slate-300"
                  }`}
                />
                <span className={`text-[9px] font-semibold ${isOnline ? "text-emerald-600" : "text-slate-400"}`}>
                  {isOnline ? "OK" : "STANDBY"}
                </span>
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
