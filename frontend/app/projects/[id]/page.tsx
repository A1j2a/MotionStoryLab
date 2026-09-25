"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Header } from "@/components/Header";
import { PipelineStepper } from "@/components/PipelineStepper";
import { LiveTerminal } from "@/components/LiveTerminal";
import { SeoHub } from "@/components/SeoHub";
import { api } from "@/lib/api";
import { Project, Scene, Character, Job, Asset } from "@/lib/types";
import {
  Clapperboard,
  Users2,
  Cpu,
  FolderArchive,
  ArrowLeft,
  Play,
  RotateCcw,
  Sparkles,
  Music,
  CheckCircle,
  Clock,
  Terminal,
  Search,
  Film,
  Download,
} from "lucide-react";

export default function ProjectDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"seo" | "scenes" | "characters" | "assets" | "logs">("seo");
  const [generating, setGenerating] = useState(false);

  const loadProject = async () => {
    if (!id) return;
    try {
      const data = await api.getProject(id);
      setProject(data);
    } catch (err) {
      console.error("Error loading project:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProject();
  }, [id]);

  // Live polling while project is actively processing
  useEffect(() => {
    const isProcessing =
      project?.status === "PROCESSING" ||
      (project?.jobs && project.jobs.length > 0 && ["PLANNING", "AUDIO_GENERATION", "RENDERING", "COMPOSITING"].includes(project.jobs[0].status));

    if (!isProcessing) return;

    const interval = setInterval(() => {
      loadProject();
    }, 2500);

    return () => clearInterval(interval);
  }, [id, project?.status, project?.jobs]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await api.generateProject(id);
      await loadProject();
    } catch (err: any) {
      alert("Generation failed to start: " + err.message);
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="p-16 text-center text-[#6E6E73] text-sm flex flex-col items-center justify-center space-y-3">
        <Sparkles className="w-6 h-6 text-[#FF6B00] animate-spin" />
        <span>Loading project details...</span>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="p-16 text-center space-y-4">
        <p className="text-rose-500 font-semibold">Project not found.</p>
        <Link
          href="/projects"
          className="text-xs text-[#EA580C] hover:underline font-semibold"
        >
          Return to Projects
        </Link>
      </div>
    );
  }

  const latestJob = project.jobs && project.jobs.length > 0 ? project.jobs[0] : null;

  return (
    <>
      <Header
        title={project.title}
        subtitle={`${project.video_type} • ${project.duration_min}-${project.duration_max} Minutes • ${project.visual_style}`}
      />

      <main className="p-8 space-y-6 flex-1 max-w-6xl mx-auto w-full">
        {/* Back Link */}
        <Link
          href="/projects"
          className="inline-flex items-center gap-1.5 text-xs text-[#6E6E73] hover:text-[#1D1D1F] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Projects</span>
        </Link>

        {/* Project Hero Card */}
        <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 shadow-xs space-y-5">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-md bg-[#FFF7ED] text-[#C2410C] border border-[#FED7AA]">
                  Status: {project.status}
                </span>
                <span className="text-[10px] font-semibold text-[#86868B] uppercase">
                  Target: {project.target_age}
                </span>
              </div>
              <h1 className="text-2xl font-bold text-[#1D1D1F] tracking-tight">
                {project.title}
              </h1>
              <p className="text-xs text-[#6E6E73] max-w-3xl leading-relaxed">
                {project.topic}
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleGenerate}
                disabled={generating || latestJob?.status === "RENDERING"}
                className="inline-flex items-center gap-2 bg-gradient-to-r from-[#FF6B00] to-[#EA580C] hover:opacity-95 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shadow-md shadow-orange-500/20 disabled:opacity-50 cursor-pointer"
              >
                <Sparkles className={`w-4 h-4 ${generating ? "animate-spin" : ""}`} />
                <span>
                  {generating
                    ? "Starting Pipeline..."
                    : latestJob?.progress === 100
                    ? "Re-generate Video"
                    : "Start Video Generation"}
                </span>
              </button>

              <Link
                href="/approval"
                className="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition-colors shadow-sm cursor-pointer"
              >
                <CheckCircle className="w-4 h-4" />
                <span>Review & Approve</span>
              </Link>
            </div>
          </div>

          {/* Prominent Visual Pipeline Stepper */}
          {latestJob && (
            <PipelineStepper
              status={latestJob.status}
              step={latestJob.current_step}
              progress={latestJob.progress}
            />
          )}
        </div>

        {/* Embedded 1080p Video Player Card (If video is ready) */}
        {(project.status === "READY" || project.status === "APPROVED" || project.assets?.some((a) => a.asset_type === "final_video")) && (
          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-[#FFF7ED] border border-[#FED7AA] flex items-center justify-center text-[#EA580C]">
                  <Film className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-[#1D1D1F] uppercase tracking-wider">
                    Full 1080p Master Video Player
                  </h3>
                  <p className="text-xs text-[#6E6E73]">
                    Watch full preschool animation with chime orchestra and synchronized subtitles
                  </p>
                </div>
              </div>

              <a
                href={`http://127.0.0.1:8000/api/v1/projects/${project.id}/video`}
                download={`${project.title}.mp4`}
                className="inline-flex items-center gap-1.5 bg-[#FFF7ED] hover:bg-[#FFEDD5] text-[#C2410C] border border-[#FED7AA] text-xs font-semibold px-3.5 py-2 rounded-xl transition-all cursor-pointer shadow-xs"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download MP4</span>
              </a>
            </div>

            <div className="aspect-video bg-black rounded-xl overflow-hidden shadow-lg border border-[#E5E5EA]">
              <video
                controls
                playsInline
                className="w-full h-full object-contain"
                src={`http://127.0.0.1:8000/api/v1/projects/${project.id}/video`}
              />
            </div>
          </div>
        )}

        {/* Apple Segmented Control Tabs */}
        <div className="bg-[#E5E5EA]/50 p-1 rounded-2xl flex items-center gap-1 overflow-x-auto select-none">
          <button
            onClick={() => setActiveTab("seo")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
              activeTab === "seo"
                ? "bg-white text-[#1D1D1F] shadow-xs font-bold"
                : "text-[#6E6E73] hover:text-[#1D1D1F]"
            }`}
          >
            <Search className="w-3.5 h-3.5 text-[#FF6B00]" />
            <span>YouTube SEO Hub</span>
          </button>

          <button
            onClick={() => setActiveTab("scenes")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
              activeTab === "scenes"
                ? "bg-white text-[#1D1D1F] shadow-xs font-bold"
                : "text-[#6E6E73] hover:text-[#1D1D1F]"
            }`}
          >
            <Clapperboard className="w-3.5 h-3.5 text-[#FF6B00]" />
            <span>Scenes & Shots ({project.scenes?.length || 0})</span>
          </button>

          <button
            onClick={() => setActiveTab("characters")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
              activeTab === "characters"
                ? "bg-white text-[#1D1D1F] shadow-xs font-bold"
                : "text-[#6E6E73] hover:text-[#1D1D1F]"
            }`}
          >
            <Users2 className="w-3.5 h-3.5 text-[#FF6B00]" />
            <span>Character Bible ({project.characters?.length || 0})</span>
          </button>

          <button
            onClick={() => setActiveTab("assets")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
              activeTab === "assets"
                ? "bg-white text-[#1D1D1F] shadow-xs font-bold"
                : "text-[#6E6E73] hover:text-[#1D1D1F]"
            }`}
          >
            <FolderArchive className="w-3.5 h-3.5 text-[#FF6B00]" />
            <span>Assets ({project.assets?.length || 0})</span>
          </button>

          <button
            onClick={() => setActiveTab("logs")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
              activeTab === "logs"
                ? "bg-white text-[#1D1D1F] shadow-xs font-bold"
                : "text-[#6E6E73] hover:text-[#1D1D1F]"
            }`}
          >
            <Terminal className="w-3.5 h-3.5 text-[#FF6B00]" />
            <span>Live Terminal Logs</span>
          </button>
        </div>

        {/* Tab Contents */}
        {activeTab === "seo" && (
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
        )}

        {activeTab === "scenes" && (
          <div className="space-y-4">
            {!project.scenes || project.scenes.length === 0 ? (
              <div className="bg-white border border-[#E5E5EA] rounded-2xl p-12 text-center text-[#6E6E73] text-sm shadow-xs">
                No scenes generated yet. Launch the pipeline above to generate shots.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {project.scenes.map((scene) => (
                  <div
                    key={scene.id}
                    className="bg-white border border-[#E5E5EA] rounded-2xl p-5 shadow-xs space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#EA580C] font-mono">
                        Shot #{String(scene.scene_number).padStart(2, "0")} • {scene.duration}s
                      </span>
                      <span
                        className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${
                          scene.status === "COMPLETED"
                            ? "bg-emerald-100 text-emerald-800"
                            : "bg-[#FFF7ED] text-[#C2410C]"
                        }`}
                      >
                        {scene.status}
                      </span>
                    </div>

                    <div>
                      <h4 className="text-sm font-bold text-[#1D1D1F]">
                        {typeof scene.environment === "object" && scene.environment !== null
                          ? (scene.environment as any).name || (scene.environment as any).id || "Preschool Meadow"
                          : String(scene.environment || "Preschool Meadow")}
                      </h4>
                      {scene.lyrics && (
                        <p className="text-xs text-[#6E6E73] italic mt-1 bg-[#FAFAFC] border border-[#E5E5EA] p-2.5 rounded-xl">
                          "{scene.lyrics}"
                        </p>
                      )}
                    </div>

                    <div className="text-[11px] text-[#6E6E73] space-y-1">
                      <div>
                        <span className="font-semibold text-[#1D1D1F]">Characters:</span>{" "}
                        {scene.characters?.map((c: any) => typeof c === 'object' && c !== null ? c.name || c.character_id || 'Hero' : String(c)).join(", ") || "None"}
                      </div>
                      <div>
                        <span className="font-semibold text-[#1D1D1F]">Action:</span>{" "}
                        {scene.actions?.join("; ") || "Default idle animation"}
                      </div>
                      {scene.render_path && (
                        <div className="text-[10px] text-emerald-600 font-mono truncate pt-1">
                          ✓ Rendered: {scene.render_path.split("/").pop()}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "characters" && (
          <div className="space-y-4">
            {!project.characters || project.characters.length === 0 ? (
              <div className="bg-white border border-[#E5E5EA] rounded-2xl p-12 text-center text-[#6E6E73] text-sm shadow-xs">
                No 3D characters in bible yet. Launch the pipeline to generate character specifications.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {project.characters.map((char) => (
                  <div
                    key={char.id}
                    className="bg-white border border-[#E5E5EA] rounded-2xl p-5 shadow-xs space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-[#FFF7ED] text-[#C2410C]">
                        {char.type}
                      </span>
                      <span className="text-[11px] font-semibold text-[#6E6E73]">
                        {char.age}
                      </span>
                    </div>

                    <div>
                      <h3 className="font-bold text-base text-[#1D1D1F]">{char.name}</h3>
                      <p className="text-xs text-[#6E6E73] mt-1 leading-relaxed">
                        {char.appearance}
                      </p>
                    </div>

                    {char.clothing && (
                      <div className="text-xs text-[#1D1D1F]">
                        <span className="font-semibold text-[#6E6E73]">Outfit:</span>{" "}
                        {char.clothing}
                      </div>
                    )}

                    {char.colors && char.colors.length > 0 && (
                      <div className="flex items-center gap-1.5 pt-1">
                        <span className="text-[11px] text-[#6E6E73] font-medium mr-1">
                          Palette:
                        </span>
                        {char.colors.map((c, ci) => (
                          <div
                            key={ci}
                            className="w-4 h-4 rounded-full border border-black/10 shadow-xs"
                            style={{ backgroundColor: c }}
                            title={c}
                          />
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "assets" && (
          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 shadow-xs space-y-4">
            <h3 className="text-sm font-bold text-[#1D1D1F] uppercase tracking-wider">
              Project Media Assets
            </h3>
            {!project.assets || project.assets.length === 0 ? (
              <p className="text-xs text-[#6E6E73] italic">
                No assets generated yet.
              </p>
            ) : (
              <div className="divide-y divide-[#E5E5EA]">
                {project.assets.map((asset) => (
                  <div
                    key={asset.id}
                    className="py-3 flex items-center justify-between gap-4 text-xs"
                  >
                    <div className="flex items-center gap-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-[#F5F5F7] border border-[#E5E5EA] text-[#1D1D1F]">
                        {asset.asset_type}
                      </span>
                      <span className="font-mono text-[#6E6E73] text-[11px] truncate max-w-md">
                        {asset.file_path}
                      </span>
                    </div>
                    <span className="font-bold text-emerald-600 text-[11px]">
                      {asset.status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "logs" && (
          <LiveTerminal projectId={project.id} title={`Engine Logs: ${project.title}`} />
        )}
      </main>
    </>
  );
}
