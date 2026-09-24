"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { Project, Asset } from "@/lib/types";
import {
  FolderArchive,
  Film,
  Music,
  FileText,
  Video,
  Image as ImageIcon,
  Sparkles,
  Download,
} from "lucide-react";

export default function AssetsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(false);
  const [filterType, setFilterType] = useState<string>("ALL");

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
    async function loadAssets() {
      setLoading(true);
      try {
        const data = await api.getAssets(
          selectedProjectId,
          filterType === "ALL" ? undefined : filterType
        );
        setAssets(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadAssets();
  }, [selectedProjectId, filterType]);

  const assetTypes = ["ALL", "music", "vocals", "audio", "thumbnail", "subtitles", "final_video"];

  const getIcon = (type: string) => {
    switch (type) {
      case "music":
      case "vocals":
      case "audio":
        return <Music className="w-4 h-4 text-[#FF6B00]" />;
      case "thumbnail":
        return <ImageIcon className="w-4 h-4 text-pink-500" />;
      case "subtitles":
        return <FileText className="w-4 h-4 text-sky-500" />;
      default:
        return <Video className="w-4 h-4 text-[#EA580C]" />;
    }
  };

  return (
    <>
      <Header
        title="Asset Library"
        subtitle="Catalog of generated audio files, image thumbnails, subtitle files, and video renders"
      />

      <main className="p-8 space-y-6 flex-1 max-w-6xl mx-auto w-full">
        {/* Project Selector Bar */}
        <div className="bg-white border border-[#E5E5EA] p-4 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xs">
          <div className="flex items-center gap-3">
            <Film className="w-5 h-5 text-[#FF6B00]" />
            <span className="text-xs font-bold text-[#1D1D1F]">
              Active Project:
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

          {/* Filter Pills */}
          <div className="flex flex-wrap gap-1.5 select-none">
            {assetTypes.map((t) => (
              <button
                key={t}
                onClick={() => setFilterType(t)}
                className={`text-xs font-semibold px-3 py-1 rounded-xl border transition-all cursor-pointer ${
                  filterType === t
                    ? "bg-[#FFF7ED] text-[#C2410C] border-[#FED7AA] shadow-xs"
                    : "bg-white text-[#6E6E73] border-[#E5E5EA] hover:text-[#1D1D1F] hover:bg-[#F5F5F7]"
                }`}
              >
                {t.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Assets Table / List */}
        {loading ? (
          <div className="p-16 text-center text-[#6E6E73] text-sm flex flex-col items-center justify-center space-y-2">
            <Sparkles className="w-5 h-5 text-[#FF6B00] animate-spin" />
            <span>Loading asset catalog...</span>
          </div>
        ) : assets.length === 0 ? (
          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-16 text-center text-[#6E6E73] text-sm shadow-xs space-y-2">
            <FolderArchive className="w-8 h-8 text-[#86868B] mx-auto opacity-50" />
            <p>No assets found for this filter. Launch video production to populate the media library.</p>
          </div>
        ) : (
          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 shadow-xs space-y-3">
            <div className="divide-y divide-[#E5E5EA]">
              {assets.map((asset) => (
                <div
                  key={asset.id}
                  className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-[#FAFAFC] border border-[#E5E5EA] flex items-center justify-center">
                      {getIcon(asset.asset_type)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-[#1D1D1F] text-xs capitalize">
                          {asset.asset_type.replace("_", " ")}
                        </span>
                        <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                          {asset.status}
                        </span>
                      </div>
                      <span className="font-mono text-[#6E6E73] text-[11px] truncate block max-w-lg mt-0.5">
                        {asset.file_path}
                      </span>
                    </div>
                  </div>

                  <div className="text-[11px] text-[#86868B] font-mono sm:text-right">
                    {new Date(asset.created_at).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </>
  );
}
