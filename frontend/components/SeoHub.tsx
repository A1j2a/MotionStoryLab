"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { SeoData } from "@/lib/types";
import {
  Sparkles,
  Copy,
  Check,
  RefreshCw,
  Hash,
  Tag,
  Clock,
  FileText,
  Save,
  Image as ImageIcon,
  Download,
} from "lucide-react";

interface SeoHubProps {
  projectId: string;
  initialSeo?: SeoData | null;
  onSeoUpdated?: (seo: SeoData) => void;
}

export function SeoHub({ projectId, initialSeo, onSeoUpdated }: SeoHubProps) {
  const [seo, setSeo] = useState<SeoData | null>(initialSeo || null);
  const [loading, setLoading] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [activeTitle, setActiveTitle] = useState("");
  const [activeDescription, setActiveDescription] = useState("");
  const [copiedSection, setCopiedSection] = useState<string | null>(null);
  const [thumbAspect, setThumbAspect] = useState<string>("16:9");
  const [generatingThumb, setGeneratingThumb] = useState(false);
  const [thumbTimestamp, setThumbTimestamp] = useState(Date.now());
  const [saveSuccess, setSaveSuccess] = useState(false);

  const fetchSeo = async () => {
    if (!projectId) return;
    setLoading(true);
    try {
      const data = await api.getProjectSeo(projectId);
      setSeo(data);
      setActiveTitle(data.title);
      setActiveDescription(data.description);
      if (onSeoUpdated) onSeoUpdated(data);
    } catch (err) {
      console.error("Failed to load SEO data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialSeo) {
      setSeo(initialSeo);
      setActiveTitle(initialSeo.title);
      setActiveDescription(initialSeo.description);
    } else {
      fetchSeo();
    }
  }, [projectId, initialSeo]);

  const handleRegenerate = async () => {
    setRegenerating(true);
    try {
      const fresh = await api.regenerateProjectSeo(projectId);
      setSeo(fresh);
      setActiveTitle(fresh.title);
      setActiveDescription(fresh.description);
      if (onSeoUpdated) onSeoUpdated(fresh);
    } catch (err: any) {
      alert("SEO regeneration failed: " + err.message);
    } finally {
      setRegenerating(false);
    }
  };

  const handleGenerateThumb = async () => {
    setGeneratingThumb(true);
    try {
      await api.generateThumbnail(projectId, { aspect_ratio: thumbAspect });
      setThumbTimestamp(Date.now());
    } catch (err: any) {
      alert("Failed to generate thumbnail: " + err.message);
    } finally {
      setGeneratingThumb(false);
    }
  };

  const handleCopy = (text: string, sectionKey: string) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(sectionKey);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  const handleSave = async () => {
    if (!seo) return;
    try {
      const updatedSeo: SeoData = {
        ...seo,
        title: activeTitle,
        description: activeDescription,
      };
      await api.updateProject(projectId, {
        title: activeTitle,
        metadata_json: { seo: updatedSeo },
      });
      setSeo(updatedSeo);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);
      if (onSeoUpdated) onSeoUpdated(updatedSeo);
    } catch (err: any) {
      alert("Failed to save SEO metadata: " + err.message);
    }
  };

  if (loading && !seo) {
    return (
      <div className="bg-white border border-[#E5E5EA] rounded-2xl p-12 text-center text-[#6E6E73] text-sm shadow-xs">
        <RefreshCw className="w-5 h-5 animate-spin mx-auto text-[#FF6B00] mb-2" />
        Generating YouTube SEO metadata package...
      </div>
    );
  }

  return (
    <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 shadow-xs space-y-6">
      {/* Top SEO Hub Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E5E5EA]">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#FF6B00]" />
            <h3 className="text-sm font-bold text-[#1D1D1F] uppercase tracking-wider">
              YouTube SEO & Publishing Hub
            </h3>
          </div>
          <p className="text-xs text-[#6E6E73] mt-0.5">
            Preschool algorithm optimized titles, hashtags, description, tags, and chapters
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleRegenerate}
            disabled={regenerating}
            className="inline-flex items-center gap-1.5 bg-[#FFF7ED] hover:bg-[#FFEDD5] text-[#C2410C] border border-[#FED7AA] text-xs font-semibold px-3.5 py-2 rounded-xl transition-all cursor-pointer shadow-xs disabled:opacity-50"
          >
            <Sparkles className={`w-3.5 h-3.5 text-[#FF6B00] ${regenerating ? "animate-spin" : ""}`} />
            <span>{regenerating ? "Regenerating..." : "Regenerate SEO"}</span>
          </button>

          <button
            onClick={handleSave}
            className="inline-flex items-center gap-1.5 bg-gradient-to-r from-[#FF6B00] to-[#EA580C] hover:opacity-95 text-white text-xs font-semibold px-4 py-2 rounded-xl transition-all cursor-pointer shadow-md shadow-orange-500/20"
          >
            {saveSuccess ? <Check className="w-3.5 h-3.5" /> : <Save className="w-3.5 h-3.5" />}
            <span>{saveSuccess ? "Saved!" : "Save Changes"}</span>
          </button>
        </div>
      </div>

      {seo && (
        <div className="space-y-6">
          {/* 1. Title Studio */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-[#FF6B00]" />
                <span>Primary YouTube Title</span>
              </label>
              <button
                onClick={() => handleCopy(activeTitle, "title")}
                className="text-[11px] font-semibold text-[#EA580C] hover:underline flex items-center gap-1 cursor-pointer"
              >
                {copiedSection === "title" ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                <span>{copiedSection === "title" ? "Copied" : "Copy Title"}</span>
              </button>
            </div>

            <input
              type="text"
              value={activeTitle}
              onChange={(e) => setActiveTitle(e.target.value)}
              className="w-full bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl px-4 py-2.5 text-sm font-semibold text-[#1D1D1F] focus:outline-none focus:ring-2 focus:ring-[#FF6B00]/30 focus:border-[#FF6B00]"
            />

            {/* Title Variations Chips */}
            {seo.titles && seo.titles.length > 0 && (
              <div className="space-y-1.5">
                <span className="text-[10px] font-semibold text-[#86868B] uppercase tracking-wider block">
                  Click any alternative variation to apply:
                </span>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {seo.titles.map((t, idx) => (
                    <button
                      key={idx}
                      onClick={() => setActiveTitle(t)}
                      className={`text-left text-xs p-2.5 rounded-xl border transition-all cursor-pointer ${
                        activeTitle === t
                          ? "bg-[#FFF7ED] border-[#FED7AA] text-[#C2410C] font-semibold shadow-xs"
                          : "bg-[#FAFAFC] border-[#E5E5EA] text-[#6E6E73] hover:text-[#1D1D1F] hover:bg-[#F5F5F7]"
                      }`}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* 2. Hashtags & YouTube Tags */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Hashtags */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
                  <Hash className="w-3.5 h-3.5 text-[#FF6B00]" />
                  <span>Trending Hashtags</span>
                </label>
                <button
                  onClick={() => handleCopy(seo.hashtags?.join(" ") || "", "hashtags")}
                  className="text-[11px] font-semibold text-[#EA580C] hover:underline flex items-center gap-1 cursor-pointer"
                >
                  {copiedSection === "hashtags" ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                  <span>{copiedSection === "hashtags" ? "Copied" : "Copy All"}</span>
                </button>
              </div>

              <div className="flex flex-wrap gap-1.5 p-3 bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl max-h-36 overflow-y-auto">
                {seo.hashtags?.map((tag, i) => (
                  <span
                    key={i}
                    onClick={() => handleCopy(tag, `tag_${i}`)}
                    className="text-[11px] font-medium bg-white text-[#EA580C] border border-[#FED7AA] px-2 py-0.5 rounded-md hover:bg-[#FFF7ED] transition-colors cursor-pointer select-all"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            {/* Search Tags */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
                  <Tag className="w-3.5 h-3.5 text-[#FF6B00]" />
                  <span>YouTube Search Tags</span>
                </label>
                <button
                  onClick={() => handleCopy(seo.tags || "", "tags")}
                  className="text-[11px] font-semibold text-[#EA580C] hover:underline flex items-center gap-1 cursor-pointer"
                >
                  {copiedSection === "tags" ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                  <span>{copiedSection === "tags" ? "Copied" : "Copy Tags"}</span>
                </button>
              </div>

              <textarea
                rows={4}
                readOnly
                value={seo.tags || ""}
                className="w-full bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl p-3 text-xs font-mono text-[#1D1D1F] focus:outline-none select-all"
              />
            </div>
          </div>

          {/* 3. Timed Chapters & Thumbnail */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Timed Chapters */}
            <div className="md:col-span-2 space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-[#FF6B00]" />
                  <span>Timed Chapters</span>
                </label>
                <button
                  onClick={() => handleCopy(seo.chapters_formatted || "", "chapters")}
                  className="text-[11px] font-semibold text-[#EA580C] hover:underline flex items-center gap-1 cursor-pointer"
                >
                  {copiedSection === "chapters" ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                  <span>{copiedSection === "chapters" ? "Copied" : "Copy Chapters"}</span>
                </button>
              </div>

              <div className="p-3 bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl text-xs font-mono text-[#1D1D1F] space-y-1">
                {seo.chapters && seo.chapters.length > 0 ? (
                  seo.chapters.map((c, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <span className="font-bold text-[#EA580C]">{c.time}</span>
                      <span className="text-[#6E6E73]">•</span>
                      <span>{c.title}</span>
                    </div>
                  ))
                ) : (
                  <p className="text-[#86868B] italic">Chapters will compute upon scene render completion.</p>
                )}
              </div>
            </div>

            {/* Thumbnail Poster */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
                  <ImageIcon className="w-3.5 h-3.5 text-[#FF6B00]" />
                  <span>High-CTR YouTube Kids Thumbnail</span>
                </label>
                <div className="flex items-center gap-1.5">
                  <select
                    value={thumbAspect}
                    onChange={(e) => setThumbAspect(e.target.value)}
                    className="text-[10px] bg-[#FAFAFA] border border-[#E5E5EA] rounded-lg px-2 py-0.5 text-[#1D1D1F] cursor-pointer"
                  >
                    <option value="16:9">16:9 Widescreen</option>
                    <option value="9:16">9:16 Shorts</option>
                  </select>
                  <button
                    onClick={handleGenerateThumb}
                    disabled={generatingThumb}
                    className="text-[11px] font-bold text-[#EA580C] hover:text-[#C2410C] bg-[#FFF7ED] px-2.5 py-1 rounded-lg border border-[#FED7AA] flex items-center gap-1 cursor-pointer disabled:opacity-50"
                  >
                    <Sparkles className="w-3 h-3" />
                    <span>{generatingThumb ? "Rendering..." : "Generate High-CTR Cover"}</span>
                  </button>
                </div>
              </div>

              <div className="aspect-video bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl overflow-hidden relative group flex items-center justify-center">
                <img
                  key={thumbTimestamp}
                  src={`http://127.0.0.1:8000/api/v1/projects/${projectId}/thumbnail?t=${thumbTimestamp}`}
                  alt="Thumbnail Preview"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.target as HTMLElement).style.display = "none";
                  }}
                />
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                  <a
                    href={`http://127.0.0.1:8000/api/v1/projects/${projectId}/thumbnail?t=${thumbTimestamp}`}
                    download="thumbnail.jpg"
                    className="bg-white text-[#1D1D1F] px-3 py-1.5 rounded-lg text-xs font-semibold shadow-md flex items-center gap-1 hover:bg-[#F5F5F7]"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download Thumbnail</span>
                  </a>
                </div>
              </div>
            </div>
          </div>

          {/* 4. Full Formatted Description */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-[#FF6B00]" />
                <span>Full YouTube Video Description</span>
              </label>
              <button
                onClick={() => handleCopy(activeDescription, "description")}
                className="text-[11px] font-semibold text-[#EA580C] hover:underline flex items-center gap-1 cursor-pointer"
              >
                {copiedSection === "description" ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                <span>{copiedSection === "description" ? "Copied" : "Copy Description"}</span>
              </button>
            </div>

            <textarea
              rows={8}
              value={activeDescription}
              onChange={(e) => setActiveDescription(e.target.value)}
              className="w-full bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl p-3.5 text-xs text-[#1D1D1F] font-mono leading-relaxed focus:outline-none focus:ring-2 focus:ring-[#FF6B00]/30 focus:border-[#FF6B00]"
            />
          </div>
        </div>
      )}
    </div>
  );
}
