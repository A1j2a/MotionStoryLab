"use client";

import { useEffect, useState, useRef } from "react";
import { api } from "@/lib/api";
import { Terminal, Copy, Check, RefreshCw, Eye, EyeOff } from "lucide-react";

interface LiveTerminalProps {
  projectId?: string;
  title?: string;
  autoScroll?: boolean;
}

export function LiveTerminal({
  projectId,
  title = "Studio Engine Live Terminal",
}: LiveTerminalProps) {
  const [lines, setLines] = useState<string[]>([]);
  const [filterProject, setFilterProject] = useState<boolean>(false);
  const [copied, setCopied] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  const fetchLogs = async () => {
    try {
      const data = await api.getLogFile("app.log", 80);
      if (data && data.lines) {
        setLines(data.lines);
      }
    } catch (err) {
      console.error("Error fetching logs:", err);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 2500);
    return () => clearInterval(interval);
  }, [projectId]);

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines]);

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

  return (
    <div className="bg-[#1C1C1E] border border-[#2C2C2E] rounded-2xl overflow-hidden shadow-xl text-xs font-mono">
      {/* macOS Terminal Titlebar */}
      <div className="bg-[#2C2C2E] px-4 py-2.5 flex items-center justify-between border-b border-[#3A3A3C]">
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

        <div className="flex items-center gap-2">
          {projectId && (
            <button
              onClick={() => setFilterProject(!filterProject)}
              className={`px-2 py-0.5 rounded text-[10px] font-semibold transition-colors flex items-center gap-1 cursor-pointer ${
                filterProject
                  ? "bg-[#FF6B00] text-white"
                  : "bg-[#3A3A3C] text-slate-300 hover:text-white"
              }`}
            >
              {filterProject ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
              <span>{filterProject ? "Project Logs Only" : "All Engine Logs"}</span>
            </button>
          )}

          <button
            onClick={handleCopy}
            className="p-1 rounded hover:bg-[#3A3A3C] text-slate-400 hover:text-white transition-colors cursor-pointer"
            title="Copy logs"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>

          <button
            onClick={handleManualRefresh}
            className="p-1 rounded hover:bg-[#3A3A3C] text-slate-400 hover:text-white transition-colors cursor-pointer"
            title="Refresh logs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin text-[#FF6B00]" : ""}`} />
          </button>
        </div>
      </div>

      {/* Terminal Output Body */}
      <div className="p-4 h-64 overflow-y-auto space-y-1 bg-[#1C1C1E] text-slate-300 select-text">
        {displayedLines.length === 0 ? (
          <div className="text-slate-500 italic py-8 text-center">
            No live logs received yet. Launching the pipeline will stream Blender and FFmpeg engine logs here.
          </div>
        ) : (
          displayedLines.map((line, idx) => {
            let color = "text-slate-300";
            if (line.includes("ERROR") || line.includes("Exception") || line.includes("failed")) {
              color = "text-rose-400 font-semibold";
            } else if (line.includes("WARNING")) {
              color = "text-amber-400";
            } else if (line.includes("SUCCESS") || line.includes("COMPLETED") || line.includes("READY")) {
              color = "text-emerald-400 font-semibold";
            } else if (line.includes("Blender") || line.includes("Scene") || line.includes("Stage")) {
              color = "text-[#FF8533]";
            } else if (line.includes("INFO")) {
              color = "text-sky-300";
            }

            return (
              <div key={idx} className="leading-relaxed hover:bg-[#2C2C2E]/60 px-1 rounded flex gap-2">
                <span className="text-slate-600 select-none text-[10px] w-6 text-right">
                  {idx + 1}
                </span>
                <span className={`break-all ${color}`}>{line}</span>
              </div>
            );
          })
        )}
        <div ref={terminalEndRef} />
      </div>
    </div>
  );
}
