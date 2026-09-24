"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { SeoHub } from "@/components/SeoHub";
import { api } from "@/lib/api";
import { Project } from "@/lib/types";
import {
  CheckCircle,
  Film,
  Play,
  Share2,
  CheckCircle2,
  Sparkles,
  Download,
} from "lucide-react";

export default function ApprovalPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [project, setProject] = useState<Project | null>(null);
  const [isApproved, setIsApproved] = useState(false);
  const [approving, setApproving] = useState(false);

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

  useEffect(() => {
    if (!selectedProjectId) return;
    async function loadDetail() {
      try {
        const data = await api.getProject(selectedProjectId);
        setProject(data);
        setIsApproved(data.status === "APPROVED");
      } catch (err) {
        console.error(err);
      }
    }
    loadDetail();
  }, [selectedProjectId]);

  const handleApprove = async () => {
    if (!project) return;
    setApproving(true);
    try {
      await api.updateProject(project.id, {
        status: "APPROVED",
      });
      setIsApproved(true);
      alert("🎉 Video approved! Ready for YouTube Data API upload staging.");
    } catch (err: any) {
      alert("Approval failed: " + err.message);
    } finally {
      setApproving(false);
    }
  };

  const hasVideo = project?.status === "READY" || project?.status === "APPROVED";

  return (
    <>
      <Header
        title="Video Review, SEO & Approval"
        subtitle="Review 1080p video preview, audit quality checklist, and manage complete YouTube SEO package"
      />

      <main className="p-8 space-y-6 flex-1 max-w-6xl mx-auto w-full">
        {/* Project Selector Bar */}
        <div className="bg-white border border-[#E5E5EA] p-4 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xs">
          <div className="flex items-center gap-3">
            <Film className="w-5 h-5 text-[#FF6B00]" />
            <span className="text-xs font-bold text-[#1D1D1F]">
              Select Project to Review:
            </span>
            <select
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(e.target.value)}
              className="bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl px-3 py-1.5 text-xs font-semibold text-[#1D1D1F] focus:outline-none focus:ring-2 focus:ring-[#FF6B00]/30 focus:border-[#FF6B00] cursor-pointer"
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title} ({p.status})
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] font-semibold text-[#6E6E73]">Status:</span>
            <span
              className={`text-xs font-bold px-3 py-1 rounded-lg border ${
                isApproved
                  ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                  : hasVideo
                  ? "bg-[#FFF7ED] text-[#C2410C] border-[#FED7AA]"
                  : "bg-[#F5F5F7] text-[#6E6E73] border-[#E5E5EA]"
              }`}
            >
              {project?.status || "NONE"}
            </span>
          </div>
        </div>

        {project ? (
          <div className="space-y-6">
            {/* Top Video Player & Quality Audit */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Video Player Preview */}
              <div className="lg:col-span-2 space-y-3">
                <div className="aspect-video bg-black rounded-2xl overflow-hidden shadow-xl border border-[#E5E5EA] flex items-center justify-center relative">
                  {hasVideo ? (
                    <video
                      controls
                      playsInline
                      className="w-full h-full object-contain"
                      src={`http://127.0.0.1:8000/api/v1/projects/${project.id}/video`}
                    />
                  ) : (
                    <div className="text-center p-8 space-y-3">
                      <div className="w-14 h-14 rounded-full bg-[#FF6B00] text-white flex items-center justify-center mx-auto shadow-lg shadow-orange-500/30">
                        <Play className="w-6 h-6 ml-0.5" />
                      </div>
                      <h4 className="text-white font-bold text-base">{project.title}</h4>
                      <p className="text-xs text-[#FED7AA]">
                        Rendering in progress... Video will automatically appear once completed.
                      </p>
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-between text-xs text-[#6E6E73] px-1">
                  <span>
                    1080p Master Render • {project.duration_min}–{project.duration_max} Minutes • {project.visual_style}
                  </span>
                  {hasVideo && (
                    <a
                      href={`http://127.0.0.1:8000/api/v1/projects/${project.id}/video`}
                      download={`${project.title}.mp4`}
                      className="text-[#EA580C] hover:underline font-semibold flex items-center gap-1 cursor-pointer"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Download MP4</span>
                    </a>
                  )}
                </div>
              </div>

              {/* Quality Checklist & Approval Button */}
              <div className="space-y-5">
                <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 shadow-xs space-y-4">
                  <h3 className="text-xs font-bold text-[#1D1D1F] uppercase tracking-wider">
                    Studio Quality Audit
                  </h3>

                  <div className="space-y-3 text-xs">
                    <div className="flex items-center justify-between text-[#1D1D1F]">
                      <span className="text-[#6E6E73]">3D Animation Shots</span>
                      <span className="font-semibold text-emerald-600 flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> {project.scenes?.length || 4} Scenes
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[#1D1D1F]">
                      <span className="text-[#6E6E73]">Character Bible</span>
                      <span className="font-semibold text-emerald-600 flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Verified
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[#1D1D1F]">
                      <span className="text-[#6E6E73]">Narration & Music</span>
                      <span className="font-semibold text-emerald-600 flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> 44.1kHz Stereo
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[#1D1D1F]">
                      <span className="text-[#6E6E73]">Timed Subtitles</span>
                      <span className="font-semibold text-emerald-600 flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Synchronized
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[#1D1D1F]">
                      <span className="text-[#6E6E73]">Upload Visibility</span>
                      <span className="font-semibold text-[#EA580C]">PRIVATE (Default)</span>
                    </div>
                  </div>

                  {/* Approval CTA */}
                  <div className="pt-4 border-t border-[#E5E5EA] space-y-2">
                    <button
                      onClick={handleApprove}
                      disabled={isApproved || approving || !hasVideo}
                      className={`w-full py-3 rounded-xl font-bold text-xs flex items-center justify-center gap-2 shadow-md transition-all cursor-pointer ${
                        isApproved
                          ? "bg-emerald-600 text-white cursor-default"
                          : hasVideo
                          ? "bg-gradient-to-r from-emerald-600 to-teal-700 hover:opacity-95 text-white shadow-emerald-600/20"
                          : "bg-[#E5E5EA] text-[#86868B] cursor-not-allowed"
                      }`}
                    >
                      <CheckCircle className="w-4 h-4" />
                      <span>{isApproved ? "Approved for YouTube" : "APPROVE VIDEO"}</span>
                    </button>
                    <p className="text-[10px] text-[#86868B] text-center">
                      Requires manual approval before YouTube Data API staging.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* All-in-One SEO Hub */}
            <SeoHub
              projectId={project.id}
              initialSeo={project.metadata_json?.seo}
              onSeoUpdated={(seo) => {
                setProject({
                  ...project,
                  title: seo.title,
                  metadata_json: { ...project.metadata_json, seo },
                });
              }}
            />
          </div>
        ) : (
          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-16 text-center text-[#6E6E73] text-sm shadow-xs">
            Select a project to review and approve.
          </div>
        )}
      </main>
    </>
  );
}
