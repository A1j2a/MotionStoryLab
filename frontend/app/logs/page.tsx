"use client";

import { useEffect, useState, useRef } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import {
  Terminal,
  RefreshCw,
  Copy,
  Check,
  Pause,
  Play,
  Layers,
  Cpu,
  Server,
  Zap,
  PowerOff,
} from "lucide-react";

export default function LogsPage() {
  const [selectedFile, setSelectedFile] = useState<string>("app.log");
  const [logLines, setLogLines] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [copied, setCopied] = useState(false);
  const [availableLogs, setAvailableLogs] = useState<Array<{ filename: string; exists: boolean; size_bytes: number }>>([]);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  const LOG_OPTIONS = [
    { name: "app.log", label: "Studio Core (FastAPI)", desc: "Main Orchestration & Database Logs" },
    { name: "ai.log", label: "AI Planning / OpenRouter", desc: "Topic Discovery, Lyrics & Storyboard" },
    { name: "render.log", label: "Storybook 3D Engine", desc: "3D Animation Frames & Camera Paths" },
    { name: "ffmpeg.log", label: "FFmpeg Compositor", desc: "Video Concat & Audio Muxing Stream" },
    { name: "tts.log", label: "Kokoro Voice Engine", desc: "Neural TTS Audio Synthesis" },
    { name: "ollama.log", label: "Ollama Local AI", desc: "Local LLaMA GPU Inference" },
    { name: "comfyui.log", label: "ComfyUI Media Daemon", desc: "Diffusion & Image Workflow" },
    { name: "n8n.log", label: "n8n Automation", desc: "Workflow Integration Hooks" },
  ];

  const fetchAvailable = async () => {
    try {
      const data = await api.getLogs();
      if (data && data.logs) {
        setAvailableLogs(data.logs);
      }
    } catch {
      // offline
    }
  };

  const fetchLogs = async () => {
    try {
      const data = await api.getLogFile(selectedFile, 200);
      setLogLines(data.lines || []);
    } catch (err: any) {
      setLogLines([`Failed to fetch log: ${err.message}`]);
    }
  };

  useEffect(() => {
    fetchAvailable();
    fetchLogs();
  }, [selectedFile]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(fetchLogs, 2000);
    return () => clearInterval(interval);
  }, [autoRefresh, selectedFile]);

  useEffect(() => {
    if (autoRefresh) {
      terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [logLines, autoRefresh]);

  const handleCopy = () => {
    navigator.clipboard.writeText(logLines.join("\n"));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatLineColor = (text: string) => {
    const lower = text.toLowerCase();
    if (lower.includes("error") || lower.includes("failed") || lower.includes("exception") || lower.includes("traceback")) {
      return "text-red-400";
    }
    if (lower.includes("warn") || lower.includes("caution")) {
      return "text-amber-300";
    }
    if (lower.includes("success") || lower.includes("completed") || lower.includes("verified") || lower.includes("passed") || lower.includes("200 ok")) {
      return "text-emerald-400";
    }
    if (lower.includes("step") || lower.includes("stage") || lower.includes("starting") || lower.includes("generating") || lower.includes("rendering")) {
      return "text-cyan-300 font-semibold";
    }
    return "text-slate-300";
  };

  return (
    <>
      <Header
        title="Live Diagnostic & Tool Engine Logs"
        subtitle="Real-time multi-tool streaming terminal for FastAPI, OpenRouter, Storybook 3D, and Audio synthesis"
      />

      <main className="p-8 space-y-6 flex-1 max-w-6xl mx-auto w-full">
        {/* Log Tool Selector Bar */}
        <div className="bg-white border border-[#E5E5EA] p-4 rounded-2xl shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
            {LOG_OPTIONS.map((opt) => (
              <button
                key={opt.name}
                onClick={() => setSelectedFile(opt.name)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all cursor-pointer ${
                  selectedFile === opt.name
                    ? "bg-[#FF6B00] text-white shadow-xs"
                    : "bg-[#F5F5F7] text-[#1D1D1F] hover:bg-[#E5E5EA]"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-3 text-xs shrink-0">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-3 py-1.5 rounded-xl font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                autoRefresh
                  ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                  : "bg-slate-100 text-slate-600 border border-slate-200"
              }`}
            >
              {autoRefresh ? (
                <>
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                  <span>Live Stream ON (2s)</span>
                </>
              ) : (
                <>
                  <Pause className="w-3.5 h-3.5" />
                  <span>Stream Paused</span>
                </>
              )}
            </button>

            <button
              onClick={fetchLogs}
              className="inline-flex items-center gap-1 text-[#FF6B00] hover:text-[#EA580C] font-semibold bg-[#FFF7ED] px-3 py-1.5 rounded-xl transition-all cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Refresh</span>
            </button>

            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1 text-slate-700 hover:text-black font-semibold bg-slate-100 px-3 py-1.5 rounded-xl transition-all cursor-pointer"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? "Copied!" : "Copy"}</span>
            </button>
          </div>
        </div>

        {/* macOS Terminal Card */}
        <div className="bg-[#1C1C1E] border border-[#2C2C2E] rounded-2xl shadow-xl overflow-hidden flex flex-col font-mono text-xs">
          <div className="bg-[#2C2C2E] px-4 py-3 flex items-center justify-between border-b border-[#3A3A3C]">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-[#FF5F56] inline-block shadow-xs" />
              <span className="w-3 h-3 rounded-full bg-[#FFBD2E] inline-block shadow-xs" />
              <span className="w-3 h-3 rounded-full bg-[#27C93F] inline-block shadow-xs" />
              <span className="ml-3 text-slate-300 text-[11px] font-semibold flex items-center gap-2">
                <Terminal className="w-3.5 h-3.5 text-[#FF6B00]" />
                <span>terminal://logs/{selectedFile}</span>
                <span className="text-[10px] text-slate-400 font-normal">
                  ({logLines.length} lines loaded)
                </span>
              </span>
            </div>

            <div className="text-[10px] text-slate-400">
              {LOG_OPTIONS.find((o) => o.name === selectedFile)?.desc}
            </div>
          </div>

          <div className="p-4 space-y-1 max-h-[550px] overflow-y-auto leading-relaxed select-text">
            {logLines.length === 0 ? (
              <div className="text-slate-500 py-12 text-center italic">
                No log output recorded yet for &apos;{selectedFile}&apos;.
              </div>
            ) : (
              logLines.map((line, idx) => (
                <div key={idx} className="flex items-start gap-2 hover:bg-[#2C2C2E]/40 px-1 rounded">
                  <span className="text-slate-600 select-none text-[10px] w-8 shrink-0 text-right">
                    {idx + 1}
                  </span>
                  <span className={`break-all ${formatLineColor(line)}`}>{line}</span>
                </div>
              ))
            )}
            <div ref={terminalEndRef} />
          </div>
        </div>
      </main>
    </>
  );
}
