"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { Project, Scene } from "@/lib/types";
import {
  Clapperboard,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Video,
  Play,
  Film,
  Sparkles,
} from "lucide-react";

export default function ScenesPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  useEffect(() => {
    async function loadProjects() {
      try {
        const list = await api.getProjects();
        setProjects(list);
        if (list.length > 0) {
          setSelectedProjectId(list[0].id);
        }
      } catch (err) {
        console.error(err);
      }
    }
    loadProjects();
  }, []);

  useEffect(() => {
    if (!selectedProjectId) return;
    async function loadScenes() {
      setLoading(true);
      try {
        const data = await api.getScenes(selectedProjectId);
        setScenes(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadScenes();
  }, [selectedProjectId]);

  const handleRegenerate = async (sceneId: string, sceneNumber: number) => {
    try {
      await api.regenerateScene(sceneId);
      setActionMessage(`Shot #${sceneNumber} reset to PENDING for individual re-rendering.`);
      const updated = await api.getScenes(selectedProjectId);
      setScenes(updated);
      setTimeout(() => setActionMessage(null), 3000);
    } catch (err) {
      alert("Failed to reset scene");
    }
  };

  return (
    <>
      <Header
        title="Scene & Shot Director"
        subtitle="Manage 3D environment shots, character choreography, and camera movements"
      />

      <main className="p-8 space-y-6 flex-1 max-w-6xl mx-auto w-full">
        {/* Project Selector Bar */}
        <div className="bg-white border border-[#E5E5EA] p-4 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xs">
          <div className="flex items-center gap-3">
            <Film className="w-5 h-5 text-[#FF6B00]" />
            <span className="text-xs font-bold text-[#1D1D1F]">
              Select Project:
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

          <div className="text-xs font-semibold px-3 py-1 rounded-lg bg-[#FAFAFC] border border-[#E5E5EA] text-[#6E6E73]">
            Total Shots: {scenes.length}
          </div>
        </div>

        {actionMessage && (
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-semibold flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>{actionMessage}</span>
          </div>
        )}

        {/* Scene Cards Grid */}
        {loading ? (
          <div className="p-16 text-center text-[#6E6E73] text-sm flex flex-col items-center justify-center space-y-2">
            <Sparkles className="w-5 h-5 text-[#FF6B00] animate-spin" />
            <span>Loading shot list...</span>
          </div>
        ) : scenes.length === 0 ? (
          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-16 text-center text-[#6E6E73] text-sm shadow-xs space-y-2">
            <Clapperboard className="w-8 h-8 text-[#86868B] mx-auto opacity-50" />
            <p>No scenes found for this project. Launch the production pipeline to generate 3D shots.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {scenes.map((scene) => (
              <div
                key={scene.id}
                className="bg-white border border-[#E5E5EA] rounded-2xl p-6 shadow-xs flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[#EA580C] font-mono">
                      Shot #{String(scene.scene_number).padStart(2, "0")} • {scene.duration}s
                    </span>
                    <span
                      className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded border ${
                        scene.status === "COMPLETED"
                          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                          : "bg-[#FFF7ED] text-[#C2410C] border-[#FED7AA]"
                      }`}
                    >
                      {scene.status}
                    </span>
                  </div>

                  <div>
                    <h3 className="font-bold text-base text-[#1D1D1F]">
                      {scene.environment}
                    </h3>
                    {scene.lyrics && (
                      <p className="text-xs text-[#6E6E73] italic mt-1 bg-[#FAFAFC] border border-[#E5E5EA] p-3 rounded-xl">
                        "{scene.lyrics}"
                      </p>
                    )}
                  </div>

                  <div className="space-y-1.5 text-xs text-[#6E6E73]">
                    <div>
                      <span className="font-semibold text-[#1D1D1F]">Characters:</span>{" "}
                      {scene.characters?.join(", ") || "None"}
                    </div>
                    <div>
                      <span className="font-semibold text-[#1D1D1F]">Actions:</span>{" "}
                      {scene.actions?.join("; ") || "Idle motion"}
                    </div>
                    {scene.camera && (
                      <div>
                        <span className="font-semibold text-[#1D1D1F]">Camera:</span>{" "}
                        {scene.camera.movement || "tracking_forward"} (FOV: {scene.camera.fov || 45}°)
                      </div>
                    )}
                  </div>
                </div>

                <div className="pt-3 border-t border-[#E5E5EA] flex items-center justify-between text-xs">
                  {scene.render_path ? (
                    <span className="text-emerald-600 font-mono text-[11px] truncate max-w-[200px]">
                      ✓ {scene.render_path.split("/").pop()}
                    </span>
                  ) : (
                    <span className="text-[#86868B] text-[11px]">Render pending</span>
                  )}

                  <button
                    onClick={() => handleRegenerate(scene.id, scene.scene_number)}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#EA580C] hover:text-[#C2410C] transition-colors cursor-pointer"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Reset Shot</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
