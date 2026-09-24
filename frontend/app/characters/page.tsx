"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { Project, Character } from "@/lib/types";
import { Users2, Film, Palette, Sparkles, Volume2 } from "lucide-react";

export default function CharactersPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [characters, setCharacters] = useState<Character[]>([]);
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
    async function loadCharacters() {
      setLoading(true);
      try {
        const data = await api.getCharacters(selectedProjectId);
        setCharacters(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadCharacters();
  }, [selectedProjectId]);

  return (
    <>
      <Header
        title="Character Bible Library"
        subtitle="Consistent recurring 3D character profiles, animations, and voice assignments"
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
            Bible Characters: {characters.length}
          </div>
        </div>

        {/* Character Cards Grid */}
        {loading ? (
          <div className="p-16 text-center text-[#6E6E73] text-sm flex flex-col items-center justify-center space-y-2">
            <Sparkles className="w-5 h-5 text-[#FF6B00] animate-spin" />
            <span>Loading 3D character bible...</span>
          </div>
        ) : characters.length === 0 ? (
          <div className="bg-white border border-[#E5E5EA] rounded-2xl p-16 text-center text-[#6E6E73] text-sm shadow-xs space-y-2">
            <Users2 className="w-8 h-8 text-[#86868B] mx-auto opacity-50" />
            <p>No characters in bible yet for this project. Launch the pipeline to generate 3D models.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {characters.map((char) => (
              <div
                key={char.id}
                className="bg-white border border-[#E5E5EA] rounded-2xl p-6 shadow-xs flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded bg-[#FFF7ED] text-[#C2410C] border border-[#FED7AA]">
                      {char.type}
                    </span>
                    <span className="text-xs font-semibold text-[#6E6E73]">
                      {char.age || "Kid"}
                    </span>
                  </div>

                  <div>
                    <h3 className="font-bold text-lg text-[#1D1D1F]">{char.name}</h3>
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

                  {char.personality && (
                    <div className="text-xs text-[#1D1D1F]">
                      <span className="font-semibold text-[#6E6E73]">Personality:</span>{" "}
                      {char.personality}
                    </div>
                  )}

                  {/* Animation Actions */}
                  {char.animation_set && char.animation_set.length > 0 && (
                    <div className="space-y-1 pt-1">
                      <span className="text-[10px] font-bold text-[#86868B] uppercase tracking-wider block">
                        Rig Animations:
                      </span>
                      <div className="flex flex-wrap gap-1">
                        {char.animation_set.map((anim, ai) => (
                          <span
                            key={ai}
                            className="text-[10px] bg-[#FAFAFC] border border-[#E5E5EA] text-[#1D1D1F] px-2 py-0.5 rounded-md"
                          >
                            {anim}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Footer Palette */}
                <div className="pt-3 border-t border-[#E5E5EA] flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <Palette className="w-3.5 h-3.5 text-[#86868B]" />
                    {char.colors && char.colors.length > 0 ? (
                      char.colors.map((c, ci) => (
                        <div
                          key={ci}
                          className="w-4 h-4 rounded-full border border-black/10 shadow-xs"
                          style={{ backgroundColor: c }}
                          title={c}
                        />
                      ))
                    ) : (
                      <span className="text-[11px] text-[#86868B]">Default palette</span>
                    )}
                  </div>

                  {char.voice && (
                    <span className="text-[11px] font-semibold text-[#EA580C] flex items-center gap-1">
                      <Volume2 className="w-3 h-3" />
                      {char.voice}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
