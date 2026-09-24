"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { Terminal, RefreshCw, AlertCircle, FileText, CheckCircle2 } from "lucide-react";

export default function LogsPage() {
  const [selectedFile, setSelectedFile] = useState<string>("app.log");
  const [logLines, setLogLines] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const LOG_OPTIONS = [
    { name: "app.log", desc: "FastAPI Backend Engine" },
    { name: "ai.log", desc: "Script & Story Planning" },
    { name: "blender.log", desc: "Blender 3D Render Engine" },
    { name: "ffmpeg.log", desc: "FFmpeg Compositing Engine" },
    { name: "audio.log", desc: "Multi-Track Synthesizer" },
  ];

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await api.getLogFile(selectedFile, 150);
      setLogLines(data.lines || []);
    } catch (err: any) {
      console.error(err);
      setLogLines([`Failed to fetch log: ${err.message}`]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [selectedFile]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(fetchLogs, 4000);
    return () => clearInterval(interval);
  }, [autoRefresh, selectedFile]);

  return (
    <>
      <Header
        title="Diagnostic & Engine Logs"
        subtitle="Real-time log viewer for pipeline debugging, Blender 3D render frames, and audio synthesis"
      />

      <main className="p-8 space-y-6 flex-1 max-w-6xl mx-auto w-full">
        {/* Log Selector Bar */}
        <div className="bg-white border border-[#E5E5EA] p-4 rounded-2xl shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-2 overflow-x-auto">
            {LOG_OPTIONS.map((opt) => (
              <button
                key={opt.name}
                onClick={() => setSelectedFile(opt.name)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  selectedFile === opt.name
                    ? "bg-[#FF6B00] text-white shadow-sm"
                    : "bg-[#F5F5F7] text-[#1D1D1F] hover:bg-[#E5E5EA]"
                }`}
              >
                {opt.name}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-4 text-xs">
            <label className="flex items-center gap-2 cursor-pointer text-[#86868B] font-medium">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="accent-[#FF6B00] rounded"
              />
              <span>Live stream (4s)</span>
            </label>

            <button
              onClick={fetchLogs}
              disabled={loading}
              className="inline-flex items-center gap-1.5 text-[#FF6B00] hover:text-[#EA580C] font-semibold bg-[#FFF7ED] px-3 py-1.5 rounded-xl transition-all"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* macOS Terminal Card */}
        <div className="bg-[#1C1C1E] border border-[#2C2C2E] rounded-2xl shadow-lg overflow-hidden flex flex-col font-mono text-xs">
          <div className="bg-[#2C2C2E] px-4 py-3 flex items-center justify-between border-b border-[#3A3A3C]">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-[#FF5F56] inline-block shadow-sm" />
              <span className="w-3 h-3 rounded-full bg-[#FFBD2E] inline-block shadow-sm" />
              <span className="w-3 h-3 rounded-full bg-[#27C93F] inline-block shadow-sm" />
              <span className="ml-3 text-[#A1A1A6] text-[11px] font-semibold">
                {selectedFile} — tail -n 150
              </span>
            </div>
            <div className="flex items-center gap-2 text-[11px] text-[#86868B]">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>{logLines.length} lines</span>
            </div>
          </div>

          <div className="p-5 overflow-y-auto max-h-[520px] space-y-1 text-[#E5E5EA] select-text bg-[#1C1C1E]">
            {logLines.length === 0 ? (
              <p className="text-[#86868B] italic py-8 text-center font-sans">
                Log file is empty or pending initialization.
              </p>
            ) : (
              logLines.map((line, idx) => (
                <div
                  key={idx}
                  className={`leading-relaxed break-all ${
                    line.includes("ERROR")
                      ? "text-rose-400 bg-rose-950/30 px-1 rounded"
                      : line.includes("WARNING")
                      ? "text-amber-300"
                      : line.includes("INFO")
                      ? "text-slate-200"
                      : line.includes("STEP") || line.includes("SUCCESS") || line.includes("PIPELINE")
                      ? "text-[#FF8A3D] font-semibold"
                      : "text-[#A1A1A6]"
                  }`}
                >
                  <span className="text-[#636366] select-none mr-3 inline-block w-8 text-right">
                    {idx + 1}
                  </span>
                  {line}
                </div>
              ))
            )}
          </div>
        </div>
      </main>
    </>
  );
}
