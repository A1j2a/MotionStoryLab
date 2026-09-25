"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { JobProgressBar } from "@/components/JobProgressBar";
import { PipelineStepper } from "@/components/PipelineStepper";
import { LiveTerminal } from "@/components/LiveTerminal";
import { api } from "@/lib/api";
import { Project, Job } from "@/lib/types";
import { Film, RotateCcw, Clock, AlertTriangle, CheckCircle2, Play, Terminal, Activity } from "lucide-react";

export default function RenderPipelinePage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [retrying, setRetrying] = useState<string | null>(null);

  useEffect(() => {
    async function loadProjects() {
      try {
        const list = await api.getProjects();
        setProjects(list);
        if (list.length > 0) setSelectedProjectId(list[0].id);
      } catch (err) {
        console.error(err);
      }
    }
    loadProjects();
  }, []);

  const loadJobs = async () => {
    if (!selectedProjectId) return;
    try {
      const data = await api.getJobs(selectedProjectId);
      setJobs(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadJobs();
    const interval = setInterval(loadJobs, 4000);
    return () => clearInterval(interval);
  }, [selectedProjectId]);

  const handleRetry = async (jobId: string) => {
    setRetrying(jobId);
    try {
      await api.retryJob(jobId);
      loadJobs();
    } catch (err: any) {
      alert("Failed to retry job: " + err.message);
    } finally {
      setRetrying(null);
    }
  };

  const activeProject = projects.find((p) => p.id === selectedProjectId);
  const latestJob = jobs[0];

  return (
    <>
      <Header
        title="Render & Pipeline Monitor"
        subtitle="Monitor sequential orchestration across Pixar-grade Storybook 3D / Wan, multi-track audio, and FFmpeg"
      />

      <main className="p-8 space-y-6 flex-1 max-w-6xl mx-auto w-full">
        {/* Project Selector Bar */}
        <div className="bg-white border border-[#E5E5EA] p-4 rounded-2xl shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[#FFF7ED] text-[#FF6B00] flex items-center justify-center">
              <Film className="w-4 h-4" />
            </div>
            <span className="text-xs font-semibold text-[#1D1D1F]">
              Active Project:
            </span>
            <select
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(e.target.value)}
              className="bg-[#F5F5F7] border border-[#E5E5EA] rounded-xl px-3 py-1.5 text-xs text-[#1D1D1F] font-medium focus:outline-none focus:ring-2 focus:ring-[#FF6B00]/30"
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title} ({p.duration_min || 1} min)
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-xs text-[#86868B] font-medium">
              Apple Silicon M4 Orchestration: Active
            </span>
          </div>
        </div>

        {/* Visual Pipeline Stepper */}
        {latestJob && (
          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-bold text-[#1D1D1F]">Active Pipeline Progression</h2>
              <span className="text-xs font-mono text-[#86868B]">Step: {latestJob.current_step || "INIT"} ({latestJob.progress}%)</span>
            </div>
            <PipelineStepper status={latestJob.status} step={latestJob.current_step} progress={latestJob.progress} />
          </div>
        )}

        {/* Live Terminal Streaming */}
        <LiveTerminal />

        {/* Jobs List */}
        <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-[#1D1D1F]">Pipeline Execution History</h2>
              <p className="text-xs text-[#86868B]">Sequential job attempts, durations, and error recovery</p>
            </div>
            <span className="text-xs font-medium text-[#86868B]">
              Total Jobs: {jobs.length}
            </span>
          </div>

          {jobs.length === 0 ? (
            <div className="text-center py-10 border border-dashed border-[#E5E5EA] rounded-xl bg-[#FAFAFA]">
              <Clock className="w-8 h-8 text-[#86868B] mx-auto mb-2 opacity-50" />
              <p className="text-xs font-semibold text-[#1D1D1F]">No jobs registered for this project yet.</p>
              <p className="text-[11px] text-[#86868B] mt-1">Start generation from the project page or Studio dashboard.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {jobs.map((job) => (
                <div
                  key={job.id}
                  className="bg-[#FAFAFA] border border-[#E5E5EA] rounded-xl p-5 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-bold text-[#FF6B00]">
                          Job: {job.id.slice(0, 8)}...
                        </span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          job.status === "COMPLETED" ? "bg-emerald-50 text-emerald-600 border border-emerald-200" :
                          job.status === "FAILED" ? "bg-rose-50 text-rose-600 border border-rose-200" :
                          "bg-orange-50 text-[#FF6B00] border border-orange-200"
                        }`}>
                          {job.status}
                        </span>
                      </div>
                      <p className="text-[11px] text-[#86868B] mt-0.5">
                        Started: {new Date(job.created_at).toLocaleString()}
                      </p>
                    </div>

                    {job.status === "FAILED" && (
                      <button
                        onClick={() => handleRetry(job.id)}
                        disabled={retrying === job.id}
                        className="inline-flex items-center gap-1.5 bg-[#FF6B00] hover:bg-[#EA580C] text-white text-xs font-semibold px-3 py-1.5 rounded-lg shadow-sm transition-colors"
                      >
                        <RotateCcw className={`w-3.5 h-3.5 ${retrying === job.id ? "animate-spin" : ""}`} />
                        <span>Retry From Last Step</span>
                      </button>
                    )}
                  </div>

                  <JobProgressBar
                    status={job.status}
                    step={job.current_step}
                    progress={job.progress}
                    error={job.error}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </>
  );
}
