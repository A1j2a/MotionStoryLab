"use client";

import { useState } from "react";
import { ContentPackage } from "@/lib/types";
import { api } from "@/lib/api";
import {
  Sparkles,
  Music,
  Mic,
  Users2,
  FileText,
  Save,
  RotateCcw,
  CheckCircle2,
  Layers,
  Palette,
  HelpCircle,
  Copy,
  Check,
  Tag,
  Hash,
} from "lucide-react";

interface ContentPackageEditorProps {
  projectId: string;
  initialPackage: ContentPackage;
  onSaved: (pkg: ContentPackage) => void;
}

export function ContentPackageEditor({
  projectId,
  initialPackage,
  onSaved,
}: ContentPackageEditorProps) {
  const [pkg, setPkg] = useState<ContentPackage>(initialPackage);
  const [saving, setSaving] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  // Copy status feedback
  const [copiedSection, setCopiedSection] = useState<string | null>(null);

  const copyToClipboard = (text: string, sectionName: string) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopiedSection(sectionName);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  const handleSave = async () => {
    setSaving(true);
    setSavedSuccess(false);
    try {
      const saved = await api.saveContentPackage(projectId, {
        ...pkg,
        approved_lyrics: pkg.lyrics_full,
      });
      setPkg(saved);
      setSavedSuccess(true);
      onSaved(saved);
      setTimeout(() => setSavedSuccess(false), 3500);
    } catch (err: any) {
      alert("Failed to save content package: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleRegenerateLyrics = async () => {
    setRegenerating(true);
    try {
      const updated = await api.regenerateLyrics(projectId);
      setPkg(updated);
    } catch (err: any) {
      alert("Failed to regenerate lyrics: " + err.message);
    } finally {
      setRegenerating(false);
    }
  };

  const formattedCharacters = pkg.characters?.map(c => `• ${c.name} (${c.species || c.type || 'Character'}): ${c.appearance}`).join("\n") || "";
  const formattedTags = pkg.tags?.join(", ") || "";
  const formattedHashtags = pkg.hashtags?.map(h => h.startsWith("#") ? h : `#${h}`).join(" ") || "";

  return (
    <div className="bg-white border border-[#E5E5EA] rounded-3xl p-6 shadow-xs space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-[#E5E5EA]">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-50 text-blue-800 border border-blue-200">
            <FileText className="w-3.5 h-3.5 text-blue-600" />
            <span>Step 2 • Complete Content Package & Approved Lyrics</span>
          </div>
          <h2 className="text-lg font-bold text-[#1D1D1F]">
            Review & Edit Video Content Package (Source of Truth)
          </h2>
          <p className="text-xs text-[#6E6E73]">
            The approved lyrics below are the definitive source of truth for downstream Song and 3D Scene generation.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleRegenerateLyrics}
            disabled={regenerating}
            className="inline-flex items-center gap-1.5 bg-[#FAFAFC] hover:bg-[#F5F5F7] text-[#1D1D1F] border border-[#E5E5EA] text-xs font-semibold px-4 py-2.5 rounded-xl transition-colors cursor-pointer disabled:opacity-50"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${regenerating ? "animate-spin" : ""}`} />
            <span>Regenerate Lyrics</span>
          </button>

          <button
            onClick={handleSave}
            disabled={saving}
            className="inline-flex items-center gap-2 bg-gradient-to-r from-[#FF6B00] to-[#EA580C] hover:opacity-95 text-white text-xs font-bold px-5 py-2.5 rounded-xl shadow-md shadow-orange-500/20 transition-all cursor-pointer disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? "Saving..." : "Save Approved Content"}</span>
          </button>
        </div>
      </div>

      {savedSuccess && (
        <div className="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-semibold flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>Approved lyrics and Character Bible successfully saved as Source of Truth!</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Metadata, Story Concept & Character Bible */}
        <div className="space-y-4">
          {/* Title with Copy Button */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-[#1D1D1F]">Video Title (SEO Optimized)</label>
              <button
                type="button"
                onClick={() => copyToClipboard(pkg.title, "title")}
                className="text-[11px] text-[#FF6B00] hover:text-[#EA580C] flex items-center gap-1 font-semibold cursor-pointer"
              >
                {copiedSection === "title" ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                <span>{copiedSection === "title" ? "Copied!" : "Copy Title"}</span>
              </button>
            </div>
            <input
              type="text"
              value={pkg.title}
              onChange={(e) => setPkg({ ...pkg, title: e.target.value })}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAFAFC] border border-[#E5E5EA] text-xs font-semibold text-[#1D1D1F] focus:outline-none focus:border-[#FF6B00]"
            />
          </div>

          {/* Story Concept with Copy Button */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-[#1D1D1F]">Story Concept</label>
              <button
                type="button"
                onClick={() => copyToClipboard(pkg.story_concept, "story")}
                className="text-[11px] text-[#FF6B00] hover:text-[#EA580C] flex items-center gap-1 font-semibold cursor-pointer"
              >
                {copiedSection === "story" ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                <span>{copiedSection === "story" ? "Copied!" : "Copy Concept"}</span>
              </button>
            </div>
            <textarea
              rows={3}
              value={pkg.story_concept}
              onChange={(e) => setPkg({ ...pkg, story_concept: e.target.value })}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FAFAFC] border border-[#E5E5EA] text-xs text-[#1D1D1F] focus:outline-none focus:border-[#FF6B00]"
            />
          </div>

          {/* Music & Voice Style with Copy Buttons */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1">
                  <Music className="w-3.5 h-3.5 text-[#FF6B00]" />
                  <span>Music Style</span>
                </label>
                <button
                  type="button"
                  onClick={() => copyToClipboard(pkg.music_style, "music")}
                  className="text-[10px] text-[#86868B] hover:text-[#1D1D1F] cursor-pointer"
                  title="Copy Music Style"
                >
                  {copiedSection === "music" ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                </button>
              </div>
              <input
                type="text"
                value={pkg.music_style}
                onChange={(e) => setPkg({ ...pkg, music_style: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-[#FAFAFC] border border-[#E5E5EA] text-[11px] text-[#1D1D1F]"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1">
                  <Mic className="w-3.5 h-3.5 text-[#FF6B00]" />
                  <span>Voice Style</span>
                </label>
                <button
                  type="button"
                  onClick={() => copyToClipboard(pkg.voice_style, "voice")}
                  className="text-[10px] text-[#86868B] hover:text-[#1D1D1F] cursor-pointer"
                  title="Copy Voice Style"
                >
                  {copiedSection === "voice" ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                </button>
              </div>
              <input
                type="text"
                value={pkg.voice_style}
                onChange={(e) => setPkg({ ...pkg, voice_style: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-[#FAFAFC] border border-[#E5E5EA] text-[11px] text-[#1D1D1F]"
              />
            </div>
          </div>

          {/* SEO Tags & Hashtags Card with Copy Buttons */}
          <div className="p-3.5 rounded-2xl bg-[#FAFAFC] border border-[#E5E5EA] space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
                <Tag className="w-3.5 h-3.5 text-[#EA580C]" />
                <span>YouTube SEO Tags & Hashtags</span>
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => copyToClipboard(formattedTags, "tags")}
                  className="text-[11px] text-[#FF6B00] hover:text-[#EA580C] font-semibold flex items-center gap-1 cursor-pointer"
                >
                  {copiedSection === "tags" ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                  <span>{copiedSection === "tags" ? "Tags Copied!" : "Copy Tags"}</span>
                </button>
                <button
                  type="button"
                  onClick={() => copyToClipboard(formattedHashtags, "hashtags")}
                  className="text-[11px] text-[#2563EB] hover:text-[#1D4ED8] font-semibold flex items-center gap-1 cursor-pointer"
                >
                  {copiedSection === "hashtags" ? <Check className="w-3 h-3 text-emerald-600" /> : <Hash className="w-3 h-3" />}
                  <span>{copiedSection === "hashtags" ? "Hashtags Copied!" : "Copy #Tags"}</span>
                </button>
              </div>
            </div>

            <div className="space-y-1.5 text-[11px]">
              <div className="text-[#6E6E73] truncate">
                <span className="font-semibold text-[#1D1D1F]">Tags:</span> {formattedTags || "Preschool, Nursery Rhymes, Kids Song, 3D Animation"}
              </div>
              <div className="text-[#2563EB] font-mono text-[10px] truncate">
                {formattedHashtags || "#NurseryRhymes #KidsSongs #PreschoolRhymes #Preschool"}
              </div>
            </div>
          </div>

          {/* Character Bible Card with Copy Button */}
          <div className="space-y-2 pt-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
                <Users2 className="w-3.5 h-3.5 text-blue-600" />
                <span>Character Bible ({pkg.characters?.length || 0} Characters)</span>
              </span>
              <button
                type="button"
                onClick={() => copyToClipboard(formattedCharacters, "characters")}
                className="text-[11px] text-[#2563EB] hover:text-[#1D4ED8] font-semibold flex items-center gap-1 cursor-pointer"
              >
                {copiedSection === "characters" ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                <span>{copiedSection === "characters" ? "Copied!" : "Copy Bible"}</span>
              </button>
            </div>
            <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
              {pkg.characters?.map((c, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-[#FAFAFC] border border-[#E5E5EA] text-xs space-y-1">
                  <div className="flex items-center justify-between font-bold text-[#1D1D1F]">
                    <span>{c.name}</span>
                    <span className="text-[10px] text-[#86868B] capitalize">{c.species || c.type}</span>
                  </div>
                  <p className="text-[11px] text-[#6E6E73]">{c.appearance}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Source of Truth Lyrics with 1-Click Copy */}
        <div className="space-y-2 flex flex-col justify-between">
          <div className="space-y-1.5 flex-1 flex flex-col">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-[#FF6B00]" />
                <span>Full Lyrics / Rhyme (Source of Truth)</span>
              </label>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => copyToClipboard(pkg.lyrics_full, "lyrics")}
                  className="px-3 py-1 rounded-xl text-xs font-bold bg-orange-100 hover:bg-orange-200 text-[#C2410C] border border-[#FED7AA] transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  {copiedSection === "lyrics" ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedSection === "lyrics" ? "Lyrics Copied!" : "Copy Full Lyrics"}</span>
                </button>
              </div>
            </div>

            <textarea
              rows={16}
              value={pkg.lyrics_full}
              onChange={(e) => setPkg({ ...pkg, lyrics_full: e.target.value })}
              className="w-full flex-1 p-4 font-mono text-xs text-[#1D1D1F] bg-[#FFFBF7] border border-orange-200 rounded-2xl focus:outline-none focus:border-[#FF6B00] leading-relaxed"
            />
          </div>

          <p className="text-[11px] text-[#86868B] italic">
            Tip: Keep stanza headers like [Verse 1], [Chorus], [Verse 2], [Outro] for optimal audio section mapping.
          </p>
        </div>
      </div>
    </div>
  );
}
