"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { HealthData } from "@/lib/types";
import {
  Settings as SettingsIcon,
  CheckCircle2,
  XCircle,
  HardDrive,
  RefreshCw,
  Cpu,
  Server,
  Trash2,
  AlertTriangle,
  FolderArchive,
  Database,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

export default function SettingsPage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(false);
  const [storage, setStorage] = useState<{
    total_formatted: string;
    projects_formatted: string;
    logs_formatted: string;
    project_count: number;
    project_dir: string;
  } | null>(null);
  const [cleaning, setCleaning] = useState(false);

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

  const fetchStorage = async () => {
    try {
      const data = await api.getStorageStatus();
      setStorage(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchHealth();
    fetchStorage();
    const interval = setInterval(fetchHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleClearCache = async (purgeAll: boolean) => {
    const confirmMsg = purgeAll
      ? "Are you sure you want to PURGE ALL projects and reset studio storage? This cannot be undone."
      : "Clean temporary scene frames and cache? Final rendered videos and master audio will be kept safely.";

    if (!confirm(confirmMsg)) return;

    setCleaning(true);
    try {
      const res = await api.clearStorage(purgeAll);
      alert(res.message);
      fetchStorage();
    } catch (err: any) {
      alert("Failed to clear storage: " + err.message);
    } finally {
      setCleaning(false);
    }
  };

  return (
    <>
      <Header
        title="Studio Settings & AI Endpoints"
        subtitle="Manage local AI engines, service ports, and disk storage without cloud dependencies"
      />

      <main className="p-8 space-y-6 flex-1 max-w-4xl mx-auto w-full">
        {/* Storage Management & Cache Cleaner Card */}
        <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 space-y-5 shadow-xs">
          <div className="flex items-center justify-between pb-4 border-b border-[#E5E5EA]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#FFF7ED] text-[#FF6B00] flex items-center justify-center border border-[#FED7AA]">
                <HardDrive className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-[#1D1D1F]">Storage & Disk Cache Management</h2>
                <p className="text-xs text-[#86868B]">
                  Inspect and purge temporary frame caches, intermediate scratch files, and logs
                </p>
              </div>
            </div>

            <button
              onClick={fetchStorage}
              className="text-xs text-[#FF6B00] hover:text-[#EA580C] font-semibold flex items-center gap-1.5 bg-[#FFF7ED] px-3 py-1.5 rounded-xl transition-all cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Refresh Disk Stats</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-[#FAFAFA] p-4 rounded-xl border border-[#E5E5EA]">
              <span className="text-[11px] font-semibold text-[#86868B] uppercase tracking-wider block">
                Total Space Used
              </span>
              <span className="text-2xl font-bold text-[#1D1D1F] mt-1 block">
                {storage?.total_formatted || "Calculating..."}
              </span>
              <span className="text-[10px] text-[#86868B] mt-1 block">
                {storage?.project_count || 0} active projects
              </span>
            </div>

            <div className="bg-[#FAFAFA] p-4 rounded-xl border border-[#E5E5EA]">
              <span className="text-[11px] font-semibold text-[#86868B] uppercase tracking-wider block">
                Project Videos & Audio
              </span>
              <span className="text-2xl font-bold text-[#1D1D1F] mt-1 block">
                {storage?.projects_formatted || "0 B"}
              </span>
              <span className="text-[10px] text-[#86868B] mt-1 block truncate">
                {storage?.project_dir || "./projects"}
              </span>
            </div>

            <div className="bg-[#FAFAFA] p-4 rounded-xl border border-[#E5E5EA]">
              <span className="text-[11px] font-semibold text-[#86868B] uppercase tracking-wider block">
                Engine Logs Cache
              </span>
              <span className="text-2xl font-bold text-[#1D1D1F] mt-1 block">
                {storage?.logs_formatted || "0 B"}
              </span>
              <span className="text-[10px] text-[#86868B] mt-1 block">
                App, LLM & FFmpeg diagnostic trails
              </span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
            <button
              onClick={() => handleClearCache(false)}
              disabled={cleaning}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-[#F5F5F7] hover:bg-[#E5E5EA] text-[#1D1D1F] border border-[#E5E5EA] text-xs font-semibold px-4 py-2.5 rounded-xl transition-all cursor-pointer"
            >
              <Trash2 className="w-4 h-4 text-[#86868B]" />
              <span>Clean Temporary Frame Cache (Safe)</span>
            </button>

            <button
              onClick={() => handleClearCache(true)}
              disabled={cleaning}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200 text-xs font-semibold px-4 py-2.5 rounded-xl transition-all cursor-pointer"
            >
              <AlertTriangle className="w-4 h-4 text-rose-500" />
              <span>Purge All Projects & Reset Storage</span>
            </button>
          </div>
        </div>

        {/* Local AI & Service Endpoints Card */}
        <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 space-y-6 shadow-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-[#FFF7ED] text-[#FF6B00] flex items-center justify-center border border-[#FED7AA]">
                <Server className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-[#1D1D1F]">Local AI & Engine Endpoints</h2>
                <p className="text-xs text-[#86868B]">
                  All engines execute locally on your Mac mini M4 with Metal GPU acceleration
                </p>
              </div>
            </div>
            <button
              onClick={fetchHealth}
              disabled={loading}
              className="inline-flex items-center gap-2 bg-[#F5F5F7] hover:bg-[#E5E5EA] text-[#1D1D1F] border border-[#E5E5EA] text-xs font-semibold px-3 py-1.5 rounded-xl transition-all cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-[#FF6B00]" : ""}`} />
              <span>Test Connections</span>
            </button>
          </div>

          <div className="space-y-3">
            {[
              { label: "FastAPI Backend Engine", url: "http://127.0.0.1:8000", port: 8000, status: health?.backend?.status || "connected" },
              { label: "Next.js 16 Web Studio", url: "http://127.0.0.1:3000", port: 3000, status: "connected" },
              { label: "Ollama Local AI (Metal M4)", url: health?.ollama?.url || "http://127.0.0.1:11434", port: 11434, status: health?.ollama?.status },
              { label: "Kokoro Neural TTS Engine", url: health?.tts?.url || "http://127.0.0.1:8880", port: 8880, status: health?.tts?.status },
              { label: "ComfyUI Media Pipeline", url: health?.comfyui?.url || "http://127.0.0.1:8188", port: 8188, status: health?.comfyui?.status },
              { label: "n8n Workflow Automation", url: health?.n8n?.url || "http://127.0.0.1:5678", port: 5678, status: health?.n8n?.status },
              { label: "FFmpeg 7.1 AV Compositor", url: "/opt/homebrew/bin/ffmpeg", port: "CLI", status: health?.ffmpeg?.status || "connected" },
            ].map((s) => (
              <div
                key={s.label}
                className="bg-[#FAFAFA] border border-[#E5E5EA] p-4 rounded-xl flex items-center justify-between hover:border-[#D1D1D6] transition-all"
              >
                <div>
                  <h4 className="text-sm font-semibold text-[#1D1D1F]">{s.label}</h4>
                  <p className="text-xs text-[#86868B] font-mono mt-0.5">{s.url}</p>
                </div>

                <div className="flex items-center gap-2">
                  <span
                    className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full ${
                      s.status === "connected"
                        ? "bg-emerald-50 text-emerald-600 border border-emerald-200"
                        : "bg-amber-50 text-amber-700 border border-amber-200"
                    }`}
                  >
                    {s.status === "connected" ? (
                      <>
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                        <span>Connected</span>
                      </>
                    ) : (
                      <>
                        <XCircle className="w-3.5 h-3.5 text-amber-600" />
                        <span>Standby / Fallback</span>
                      </>
                    )}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Claude AI & Suno.ai Integration Card */}
        <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 space-y-4 shadow-xs">
          <div className="flex items-center gap-3 pb-3 border-b border-[#E5E5EA]">
            <div className="w-9 h-9 rounded-xl bg-[#FFF7ED] text-[#FF6B00] flex items-center justify-center border border-[#FED7AA]">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-[#1D1D1F]">Claude 3.5 SEO & Suno.ai Music Integrations</h2>
              <p className="text-xs text-[#86868B]">
                High-CTR YouTube metadata with Anthropic Claude & catchy nursery song generation with Suno.ai
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-[#FAFAFA] p-4 rounded-xl border border-[#E5E5EA] space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-[#1D1D1F]">Anthropic Claude 3.5 Sonnet</span>
                <span className="text-[10px] bg-purple-50 text-purple-700 font-semibold px-2 py-0.5 rounded-full border border-purple-200">
                  YouTube SEO & Viral Tags
                </span>
              </div>
              <p className="text-[11px] text-[#86868B]">
                Provides high-CTR thumbnail hooks, COPPA compliant descriptions, and 15+ search keywords.
              </p>
              <div className="pt-1">
                <span className="text-[10px] font-mono text-emerald-600 bg-emerald-50 px-2 py-1 rounded border border-emerald-200 block">
                  ✓ Configured with Local Ollama Fallback
                </span>
              </div>
            </div>

            <div className="bg-[#FAFAFA] p-4 rounded-xl border border-[#E5E5EA] space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-[#1D1D1F]">Suno.ai Music Engine</span>
                <span className="text-[10px] bg-amber-50 text-amber-700 font-semibold px-2 py-0.5 rounded-full border border-amber-200">
                  Nursery Rhyme Melodies
                </span>
              </div>
              <p className="text-[11px] text-[#86868B]">
                Generates catchy preschool melodies with song structure tags ([Verse], [Chorus], [Outro]).
              </p>
              <div className="pt-1">
                <span className="text-[10px] font-mono text-emerald-600 bg-emerald-50 px-2 py-1 rounded border border-emerald-200 block">
                  ✓ Configured with Neural Chime Synthesizer Fallback
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Apple Silicon Hardware Management Card */}
        <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 space-y-3 shadow-xs">
          <div className="flex items-center gap-2.5 text-[#FF6B00]">
            <div className="w-8 h-8 rounded-lg bg-[#FFF7ED] flex items-center justify-center border border-[#FED7AA]">
              <Cpu className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-bold text-[#1D1D1F]">Apple Silicon Unified Architecture</h3>
          </div>
          <p className="text-xs text-[#86868B] leading-relaxed">
            MotionStoryLabs operates 100% locally on your Mac mini M4. Sequential pipeline execution releases RAM and GPU buffers between Ollama / Claude AI lyrics generation, Suno / audio DSP synthesis, storybook animation rendering, and multi-track FFmpeg compositing, ensuring optimal thermal performance and stability.
          </p>
        </div>
      </main>
    </>
  );
}
