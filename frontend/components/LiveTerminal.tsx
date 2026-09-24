"use client";

import { useEffect, useState, useRef } from "react";
import { api } from "@/lib/api";
import { Terminal, Copy, Check, RefreshCw, Eye, EyeOff, Play, Pause, Layers } from "lucide-react";

interface LiveTerminalProps {
  projectId?: string;
  title?: string;
  defaultLog?: string;
}

const AVAILABLE_LOGS = [
  { file: "app.log", label: "Studio Core (FastAPI)" },
  { file: "ai.log", label: "AI Planning & OpenRouter" },
  { file: "blender.log", label: "Blender 3D Render Engine" },
  { file: "ffmpeg.log", label: "FFmpeg Video Compositor" },
  { file: "tts.log", label: "Kokoro TTS Voice Service" },
  { file: "ollama.log", label: "Ollama Local AI" },
  { file: "comfyui.log", label: "ComfyUI Media Engine" },
  { file: "n8n.log", label: "n8n Automation Daemon" },
];

export function LiveTerminal({
  projectId,
  title = "Studio Live Engine Terminal",
  defaultLog = "app.log",
}: LiveTerminalProps) {
  const [selectedLog, setSelectedLog] = useState<string>(defaultLog);
  const [lines, setLines] = useState<string[]>([]);
  const [filterProject, setFilterProject] = useState<boolean>(false);
  const [copied, setCopied] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isStreaming, setIsStreaming] = useState(true);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  const fetchLogs = async () => {
    try {
      const data = await api.getLogFile(selectedLog, 120);
      if (data && data.lines) {
        setLines(data.lines);
      }
    } catch {
      // offline or not yet created
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [selectedLog]);

  useEffect(() => {
    if (!isStreaming) return;
    const interval = setInterval(fetchLogs, 2000);
    return () => clearInterval(interval);
  }, [isStreaming, selectedLog]);

  useEffect(() => {
    if (isStreaming) {
      terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [lines, isStreaming]);

  const displayedLines = lines.filter((line) => {
    if (!filterProject || !projectId) return true;
    return line.includes(projectId);
  });

  const handleCopy = () => {
    navigator.clipboard.writeText(displayedLines.join("\n"));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleManualRefresh = async () => {
    setIsRefreshing(true);
    await fetchLogs();
    setTimeout(() => setIsRefreshing(false), 500);
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
    if (lower.includes("openrouter") || lower.includes("blender") || lower.includes("suno") || lower.includes("fastapi")) {
      return "text-purple-300";
    }
    return "text-slate-300";
  };

  return (
    <div className="bg-[#1C1C1E] border border-[#2C2C2E] rounded-2xl overflow-hidden shadow-xl text-xs font-mono">
      {/* macOS Terminal Titlebar */}
      <div className="bg-[#2C2C2E] px-4 py-2.5 flex flex-wrap items-center justify-between border-b border-[#3A3A3C] gap-2">
        <div className="flex items-center gap-2">
          {/* Traffic Lights */}
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-[#FF5F56] border border-[#E0443E]/50" />
            <span className="w-3 h-3 rounded-full bg-[#FFBD2E] border border-[#DEA123]/50" />
            <span className="w-3 h-3 rounded-full bg-[#27C93F] border border-[#1AAB29]/50" />
          </div>

          <span className="ml-2 text-slate-300 font-semibold text-[11px] flex items-center gap-1.5">
            <Terminal className="w-3.5 h-3.5 text-[#FF6B00]" />
            <span>{title}</span>
          </span>
        </div>

        {/* Log Tool Selector Dropdown */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 bg-[#1C1C1E] px-2 py-1 rounded-lg border border-[#3A3A3C]">
            <Layers className="w-3 h-3 text-[#FF6B00]" />
            <select
              value={selectedLog}
              onChange={(e) => setSelectedLog(e.target.value)}
              className="bg-transparent text-slate-300 text-[10px] focus:outline-none cursor-pointer"
            >
              {AVAILABLE_LOGS.map((opt) => (
                <option key={opt.file} value={opt.file} className="bg-[#1C1C1E] text-slate-200">
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {projectId && (
            <button
              onClick={() => setFilterProject(!filterProject)}
              className={`px-2 py-1 rounded text-[10px] font-semibold transition-colors flex items-center gap-1 cursor-pointer ${
                filterProject
                  ? "bg-[#FF6B00] text-white"
                  : "bg-[#3A3A3C] text-slate-300 hover:text-white"
              }`}
            >
              {filterProject ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
              <span>{filterProject ? "Project Only" : "All Engine Logs"}</span>
            </button>
          )}

          {/* Stream Pause/Play */}
          <button
            onClick={() => setIsStreaming(!isStreaming)}
            className={`px-2 py-1 rounded text-[10px] font-semibold flex items-center gap-1 cursor-pointer transition-colors ${
              isStreaming
                ? "bg-emerald-950/60 text-emerald-400 border border-emerald-800"
                : "bg-amber-950/60 text-amber-400 border border-amber-800"
            }`}
            title={isStreaming ? "Pause live streaming" : "Resume live streaming"}
          >
            {isStreaming ? (
              <>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                <span>Live (2s)</span>
              </>
            ) : (
              <>
                <Pause className="w-3 h-3" />
                <span>Paused</span>
              </>
            )}
          </button>

          <button
            onClick={handleManualRefresh}
            className="p-1 rounded hover:bg-[#3A3A3C] text-slate-400 hover:text-white transition-colors cursor-pointer"
            title="Refresh logs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin text-[#FF6B00]" : ""}`} />
          </button>

          <button
            onClick={handleCopy}
            className="p-1 rounded hover:bg-[#3A3A3C] text-slate-400 hover:text-white transition-colors cursor-pointer"
            title="Copy logs"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Terminal Output Area */}
      <div className="p-4 space-y-1 max-h-72 overflow-y-auto font-mono text-[11px] leading-relaxed select-text">
        {displayedLines.length === 0 ? (
          <div className="text-slate-500 py-6 text-center italic">
            Waiting for tool activity... Log file &apos;{selectedLog}&apos; is active and ready.
          </div>
        ) : (
          displayedLines.map((line, idx) => (
            <div key={idx} className="flex items-start gap-2 hover:bg-[#2C2C2E]/40 px-1 rounded">
              <span className="text-slate-600 select-none text-[10px] w-6 shrink-0 text-right">
                {idx + 1}
              </span>
              <span className={`break-all ${formatLineColor(line)}`}>{line}</span>
            </div>
          ))
        )}
        <div ref={terminalEndRef} />
      </div>
    </div>
  );
}
