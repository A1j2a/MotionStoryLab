"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { Project } from "@/lib/types";
import {
  Film,
  PlusCircle,
  Search,
  Filter,
  Trash2,
  Clock,
  ArrowRight,
  Sparkles,
} from "lucide-react";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState("");

  const loadProjects = async (status?: string) => {
    setLoading(true);
    try {
      const data = await api.getProjects(status === "ALL" ? undefined : status);
      setProjects(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects(selectedStatus);
  }, [selectedStatus]);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    if (!confirm("Are you sure you want to delete this project?")) return;
    try {
      await api.deleteProject(id);
      setProjects(projects.filter((p) => p.id !== id));
    } catch (err) {
      alert("Failed to delete project");
    }
  };

  const filtered = projects.filter(
    (p) =>
      p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.topic.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const statuses = ["ALL", "DRAFT", "PROCESSING", "READY", "APPROVED", "COMPLETED"];

  return (
    <>
      <Header
        title="Video Projects"
        subtitle="Manage and track your local 3D animation productions"
      />

      <main className="p-8 space-y-6 flex-1 max-w-6xl mx-auto w-full">
        {/* Controls Bar */}
        <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
          {/* Search Box */}
          <div className="relative w-full md:w-80">
            <Search className="w-4 h-4 text-[#86868B] absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by title or topic..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white border border-[#E5E5EA] rounded-xl pl-10 pr-4 py-2 text-xs text-[#1D1D1F] focus:outline-none focus:ring-2 focus:ring-[#FF6B00]/30 focus:border-[#FF6B00] shadow-xs"
            />
          </div>

          {/* Status Filter Pills */}
          <div className="flex flex-wrap gap-1.5 select-none">
            {statuses.map((s) => (
              <button
                key={s}
                onClick={() => setSelectedStatus(s)}
                className={`text-xs font-semibold px-3 py-1.5 rounded-xl border transition-all cursor-pointer ${
                  selectedStatus === s
                    ? "bg-[#FFF7ED] text-[#C2410C] border-[#FED7AA] shadow-xs"
                    : "bg-white text-[#6E6E73] border-[#E5E5EA] hover:text-[#1D1D1F] hover:bg-[#F5F5F7]"
                }`}
              >
                {s}
              </button>
            ))}
          </div>

          <Link
            href="/create"
            className="flex items-center gap-2 bg-gradient-to-r from-[#FF6B00] to-[#EA580C] hover:opacity-95 text-white text-xs font-bold px-4 py-2.5 rounded-xl shadow-md shadow-orange-500/20 transition-all cursor-pointer whitespace-nowrap"
          >
            <PlusCircle className="w-4 h-4" />
            <span>New Video</span>
          </Link>
        </div>

        {/* Projects List */}
        {loading ? (
          <div className="p-16 text-center text-[#6E6E73] text-sm flex flex-col items-center justify-center space-y-2">
            <Sparkles className="w-5 h-5 text-[#FF6B00] animate-spin" />
            <span>Loading studio projects...</span>
          </div>
        ) : filtered.length === 0 ? (
          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-16 text-center text-[#6E6E73] text-sm shadow-xs space-y-4">
            <Film className="w-8 h-8 text-[#86868B] mx-auto opacity-50" />
            <p>No projects match your filter.</p>
            <Link
              href="/create"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#EA580C] hover:underline"
            >
              <span>Create your first project</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filtered.map((proj) => (
              <Link
                key={proj.id}
                href={`/projects/${proj.id}`}
                className="bg-white hover:bg-[#FAFAFC] border border-[#E5E5EA] hover:border-[#FED7AA] rounded-2xl p-5 transition-all shadow-xs group flex flex-col justify-between space-y-4 cursor-pointer"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-[#FFF7ED] text-[#C2410C] border border-[#FED7AA]">
                      {proj.status}
                    </span>
                    <button
                      onClick={(e) => handleDelete(proj.id, e)}
                      className="p-1 rounded text-[#86868B] hover:text-rose-600 hover:bg-rose-50 transition-colors"
                      title="Delete project"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div>
                    <h3 className="font-bold text-[#1D1D1F] text-base group-hover:text-[#EA580C] transition-colors leading-snug">
                      {proj.title}
                    </h3>
                    <p className="text-xs text-[#6E6E73] line-clamp-2 mt-1 leading-relaxed">
                      {proj.topic}
                    </p>
                  </div>
                </div>

                <div className="pt-3 border-t border-[#E5E5EA] space-y-2">
                  <div className="flex items-center justify-between text-[11px] text-[#6E6E73]">
                    <span>
                      {proj.video_type} • {proj.target_age}
                    </span>
                    <span className="font-mono">{proj.duration_min}–{proj.duration_max}m</span>
                  </div>

                  <div className="flex items-center justify-between text-xs pt-1 text-[#EA580C] font-semibold">
                    <span className="text-[11px] text-[#86868B] font-normal">
                      {new Date(proj.created_at).toLocaleDateString()}
                    </span>
                    <span className="flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                      Open Project →
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
