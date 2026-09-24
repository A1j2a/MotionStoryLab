"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { Sparkles, ArrowRight, Wand2 } from "lucide-react";

export default function CreateVideoPage() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    title: "",
    topic: "",
    language: "en",
    duration_min: 5,
    duration_max: 7,
    video_type: "Nursery Rhyme",
    visual_style: "3D Cartoon",
    target_age: "Kids",
    character_style: "Cute rounded 3D preschool style with vibrant colors",
    music_style: "Upbeat orchestral preschool nursery tune with bell accents",
    voice_style: "Warm cheerful animated storyteller",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.topic.trim()) {
      setError("Please enter a video topic or idea.");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const generatedTitle =
        formData.title.trim() ||
        formData.topic
          .split(" ")
          .slice(0, 6)
          .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
          .join(" ");

      const project = await api.createProject({
        ...formData,
        title: generatedTitle,
      });

      router.push(`/projects/${project.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to create video project.");
    } finally {
      setSubmitting(false);
    }
  };

  const topicPresets = [
    "Toto the Blue Train meets farm animals in the sunny meadow",
    "Five little ducks swimming across the rainbow river",
    "Barnaby Bear picking strawberries with butterflies",
    "Wheels on the colorful school bus going all through town",
  ];

  return (
    <>
      <Header
        title="Create New Video"
        subtitle="Transform an idea into an automated 3D animated nursery rhyme video"
      />

      <main className="p-8 max-w-4xl mx-auto w-full space-y-6">
        <form
          onSubmit={handleSubmit}
          className="bg-white border border-[#E5E5EA] rounded-3xl p-8 shadow-xs space-y-6"
        >
          {error && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-700 font-semibold">
              {error}
            </div>
          )}

          {/* Idea & Topic */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-[#1D1D1F] uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-[#FF6B00]" />
                <span>Video Idea or Topic (Prompt) *</span>
              </label>
              <span className="text-[11px] text-[#86868B]">Be descriptive or choose a preset</span>
            </div>

            <textarea
              rows={3}
              required
              placeholder="e.g., Friendly little steam train rolling through the sunflower valley meeting Daisy the Cow and Barnaby Bear..."
              value={formData.topic}
              onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
              className="w-full bg-[#FAFAFC] border border-[#E5E5EA] rounded-2xl p-4 text-sm font-medium text-[#1D1D1F] placeholder-[#86868B] focus:outline-none focus:ring-2 focus:ring-[#FF6B00]/30 focus:border-[#FF6B00] transition-all"
            />

            {/* Quick Presets */}
            <div className="space-y-1.5 pt-1">
              <span className="text-[10px] font-semibold text-[#86868B] uppercase tracking-wider block">
                Quick Start Presets:
              </span>
              <div className="flex flex-wrap gap-2">
                {topicPresets.map((preset, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setFormData({ ...formData, topic: preset, title: "" })}
                    className="text-left text-xs bg-[#FFF7ED] hover:bg-[#FFEDD5] border border-[#FED7AA] text-[#C2410C] font-medium px-3 py-1.5 rounded-xl transition-all cursor-pointer shadow-xs"
                  >
                    + {preset}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Optional Custom Title */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-[#1D1D1F] uppercase tracking-wider">
              Project Title (Optional)
            </label>
            <input
              type="text"
              placeholder="Leave blank for auto-generated title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl px-4 py-2.5 text-xs font-medium text-[#1D1D1F] placeholder-[#86868B] focus:outline-none focus:ring-2 focus:ring-[#FF6B00]/30 focus:border-[#FF6B00]"
            />
          </div>

          {/* Target Video Duration Selector */}
          <div className="space-y-2 pt-1">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-[#1D1D1F] uppercase tracking-wider">
                Target Video Duration *
              </label>
              <span className="text-[11px] font-semibold text-[#EA580C]">
                Selected: {formData.duration_min} Minute ({formData.duration_min * 60} Seconds)
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
              {[
                { min: 1, label: "1 Minute", desc: "60s Quick Rhyme" },
                { min: 2, label: "2 Minutes", desc: "120s Full Song" },
                { min: 3, label: "3 Minutes", desc: "180s Extended Story" },
                { min: 5, label: "5 Minutes", desc: "300s Compilation" },
              ].map((d) => (
                <button
                  key={d.min}
                  type="button"
                  onClick={() => setFormData({ ...formData, duration_min: d.min, duration_max: d.min + 1 })}
                  className={`p-3 rounded-2xl border text-left transition-all cursor-pointer ${
                    formData.duration_min === d.min
                      ? "bg-[#FFF7ED] border-[#FED7AA] shadow-xs ring-2 ring-[#FF6B00]/20"
                      : "bg-[#FAFAFC] border-[#E5E5EA] hover:bg-[#F5F5F7] text-[#6E6E73]"
                  }`}
                >
                  <div className="font-bold text-xs text-[#1D1D1F]">{d.label}</div>
                  <div className="text-[10px] text-[#86868B] mt-0.5">{d.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Style & Options Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 pt-2">
            {/* Visual Style */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-[#1D1D1F] uppercase tracking-wider">
                Visual Style
              </label>
              <select
                value={formData.visual_style}
                onChange={(e) => setFormData({ ...formData, visual_style: e.target.value })}
                className="w-full bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl px-3 py-2 text-xs font-semibold text-[#1D1D1F] focus:outline-none focus:ring-2 focus:ring-[#FF6B00]/30 focus:border-[#FF6B00] cursor-pointer"
              >
                <option value="3D Cartoon">3D Cartoon (Vibrant Low-Poly)</option>
                <option value="Claymation">Claymation (Soft Tactile)</option>
                <option value="Storybook 3D">Storybook 3D (Pastel & Gentle)</option>
              </select>
            </div>

            {/* Target Age */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-[#1D1D1F] uppercase tracking-wider">
                Target Age Group
              </label>
              <select
                value={formData.target_age}
                onChange={(e) => setFormData({ ...formData, target_age: e.target.value })}
                className="w-full bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl px-3 py-2 text-xs font-semibold text-[#1D1D1F] focus:outline-none focus:ring-2 focus:ring-[#FF6B00]/30 focus:border-[#FF6B00] cursor-pointer"
              >
                <option value="Kids">Preschool (Ages 2–5)</option>
                <option value="Babies">Toddler & Baby (Ages 0–2)</option>
                <option value="Kindergarten">Kindergarten (Ages 5–7)</option>
              </select>
            </div>

            {/* Video Type */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-[#1D1D1F] uppercase tracking-wider">
                Video Type
              </label>
              <select
                value={formData.video_type}
                onChange={(e) => setFormData({ ...formData, video_type: e.target.value })}
                className="w-full bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl px-3 py-2 text-xs font-semibold text-[#1D1D1F] focus:outline-none focus:ring-2 focus:ring-[#FF6B00]/30 focus:border-[#FF6B00] cursor-pointer"
              >
                <option value="Nursery Rhyme">Nursery Rhyme & Sing-Along</option>
                <option value="Bedtime Lullaby">Bedtime Lullaby</option>
                <option value="Educational Song">Alphabet / Counting Song</option>
              </select>
            </div>
          </div>

          {/* Submit Action */}
          <div className="pt-4 border-t border-[#E5E5EA] flex items-center justify-between">
            <span className="text-xs text-[#86868B]">
              Runs 100% locally on your Mac mini M4 with zero external paid APIs.
            </span>

            <button
              type="submit"
              disabled={submitting}
              className="inline-flex items-center gap-2 bg-gradient-to-r from-[#FF6B00] to-[#EA580C] hover:opacity-95 text-white text-xs font-bold px-6 py-3 rounded-xl shadow-md shadow-orange-500/25 transition-all cursor-pointer disabled:opacity-50"
            >
              <Wand2 className={`w-4 h-4 ${submitting ? "animate-spin" : ""}`} />
              <span>{submitting ? "Initializing Project..." : "Launch Video Production"}</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </button>
          </div>
        </form>
      </main>
    </>
  );
}
