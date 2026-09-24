"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { Project, Asset } from "@/lib/types";
import { Music, Film, Mic, Volume2, Sparkles, Disc } from "lucide-react";

export default function AudioStudioPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [audioAssets, setAudioAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(false);

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
    async function loadAudio() {
      setLoading(true);
      try {
        const allAssets = await api.getAssets(selectedProjectId);
        const filtered = allAssets.filter((a) =>
          ["audio", "music", "vocals", "sfx"].includes(a.asset_type)
        );
        setAudioAssets(filtered);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadAudio();
  }, [selectedProjectId]);

  const activeProject = projects.find((p) => p.id === selectedProjectId);

  return (
    <>
      <Header
        title="Audio Studio & Vocals"
        subtitle="Manage preschool chime melodies, narration vocal stems, and multi-track audio master"
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

          <div className="text-xs font-semibold px-3 py-1 rounded-lg bg-[#FAFAFC] border border-[#E5E5EA] text-[#6E6E73]">
            Track Stems: {audioAssets.length}
          </div>
        </div>

        {/* Project Style Info Banner */}
        {activeProject && (
          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 shadow-xs grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#FFF7ED] border border-[#FED7AA] flex items-center justify-center text-[#EA580C]">
                <Music className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] font-bold text-[#86868B] uppercase tracking-wider block">
                  Music Style
                </span>
                <span className="text-xs font-semibold text-[#1D1D1F]">
                  {activeProject.music_style || "Upbeat Preschool Nursery Chimes"}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#FFF7ED] border border-[#FED7AA] flex items-center justify-center text-[#EA580C]">
                <Mic className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] font-bold text-[#86868B] uppercase tracking-wider block">
                  Voice Style
                </span>
                <span className="text-xs font-semibold text-[#1D1D1F]">
                  {activeProject.voice_style || "Cheerful Animated Storyteller"}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#FFF7ED] border border-[#FED7AA] flex items-center justify-center text-[#EA580C]">
                <Disc className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] font-bold text-[#86868B] uppercase tracking-wider block">
                  Target Audio Spec
                </span>
                <span className="text-xs font-semibold text-[#1D1D1F]">
                  44.1 kHz • 16-bit Stereo Master
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Audio Stems Grid */}
        {loading ? (
          <div className="p-16 text-center text-[#6E6E73] text-sm flex flex-col items-center justify-center space-y-2">
            <Sparkles className="w-5 h-5 text-[#FF6B00] animate-spin" />
            <span>Loading audio studio stems...</span>
          </div>
        ) : audioAssets.length === 0 ? (
          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-16 text-center text-[#6E6E73] text-sm shadow-xs space-y-2">
            <Volume2 className="w-8 h-8 text-[#86868B] mx-auto opacity-50" />
            <p>No audio files generated yet for this project. Launch video generation to synthesize tracks.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {audioAssets.map((asset) => (
              <div
                key={asset.id}
                className="bg-white border border-[#E5E5EA] rounded-2xl p-6 shadow-xs space-y-4"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded bg-[#FFF7ED] text-[#C2410C] border border-[#FED7AA]">
                    {asset.asset_type.toUpperCase()} TRACK
                  </span>
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                    {asset.status}
                  </span>
                </div>

                <div>
                  <h4 className="font-bold text-sm text-[#1D1D1F] capitalize">
                    {asset.asset_type === "audio"
                      ? "Master Soundtrack (Vocals + Chimes)"
                      : `${asset.asset_type} Stem`}
                  </h4>
                  <p className="text-[11px] font-mono text-[#6E6E73] truncate mt-1">
                    {asset.file_path}
                  </p>
                </div>

                {/* Audio Waveform / Player */}
                <div className="bg-[#FAFAFC] border border-[#E5E5EA] p-3 rounded-xl flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2 text-xs font-semibold text-[#1D1D1F]">
                    <Volume2 className="w-4 h-4 text-[#FF6B00]" />
                    <span>Audio Stem Preview</span>
                  </div>
                  <span className="text-[11px] font-mono text-[#86868B]">44.1kHz PCM</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
