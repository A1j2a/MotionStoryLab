"use client";

import { useState, useEffect } from "react";
import {
  X,
  Copy,
  Check,
  ExternalLink,
  Download,
  UploadCloud,
  FileText,
  Tag,
  Hash,
  Sparkles,
  ShieldCheck,
  Video,
  Image as ImageIcon,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { api } from "@/lib/api";

interface YouTubeStudioModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  projectTopic?: string;
  defaultTitle?: string;
  defaultDescription?: string;
  defaultTags?: string[];
  defaultHashtags?: string[];
  thumbnailUrl?: string;
  videoUrl?: string;
}

export default function YouTubeStudioModal({
  isOpen,
  onClose,
  projectId,
  projectTopic = "",
  defaultTitle = "",
  defaultDescription = "",
  defaultTags = [],
  defaultHashtags = [],
  thumbnailUrl = "",
  videoUrl = "",
}: YouTubeStudioModalProps) {
  const [title, setTitle] = useState(defaultTitle);
  const [description, setDescription] = useState(defaultDescription);
  const [tags, setTags] = useState(defaultTags.join(", "));
  const [hashtags, setHashtags] = useState(defaultHashtags.join(" "));
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [apiUploading, setApiUploading] = useState(false);
  const [apiResult, setApiResult] = useState<{ success: boolean; message: string; url?: string } | null>(null);

  // Sync props when modal opens
  useEffect(() => {
    if (isOpen) {
      if (defaultTitle) setTitle(defaultTitle);
      if (defaultDescription) setDescription(defaultDescription);
      if (defaultTags && defaultTags.length > 0) setTags(defaultTags.join(", "));
      if (defaultHashtags && defaultHashtags.length > 0) setHashtags(defaultHashtags.join(" "));
      setApiResult(null);
    }
  }, [isOpen, defaultTitle, defaultDescription, defaultTags, defaultHashtags]);

  if (!isOpen) return null;

  const safeCopy = async (text: string): Promise<boolean> => {
    try {
      if (typeof window !== "undefined" && navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(text);
        return true;
      }
    } catch {
      // Fallback if document is not focused or permissions blocked
    }

    try {
      if (typeof document !== "undefined") {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.left = "-999999px";
        textArea.style.top = "-999999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        const successful = document.execCommand("copy");
        document.body.removeChild(textArea);
        return successful;
      }
    } catch {
      // ignore
    }
    return false;
  };

  const copyToClipboard = async (text: string, fieldName: string) => {
    await safeCopy(text);
    setCopiedField(fieldName);
    setTimeout(() => setCopiedField(null), 2500);
  };

  const handleOpenStudio = async () => {
    // Copy title safely if available
    if (title) {
      await safeCopy(title);
      setCopiedField("auto_title");
    }
    window.open("https://studio.youtube.com/channel/upload", "_blank", "noopener,noreferrer");
  };

  const handleDirectApiUpload = async () => {
    setApiUploading(true);
    setApiResult(null);
    try {
      const res = await api.uploadYouTube(projectId, "private");
      setApiResult({
        success: true,
        message: res.message || "Uploaded to YouTube Studio as Private Draft.",
        url: res.youtube_url || (res as any).video_url,
      });
    } catch (err: any) {
      setApiResult({
        success: false,
        message: err?.message || "Upload failed. Please check credentials or use YouTube Studio manual upload.",
      });
    } finally {
      setApiUploading(false);
    }
  };

  const resolvedVideoUrl = videoUrl || `http://127.0.0.1:8000/api/v1/projects/${projectId}/video`;
  const resolvedThumbUrl = thumbnailUrl || `http://127.0.0.1:8000/api/v1/projects/${projectId}/thumbnail`;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="bg-white border border-[#E5E5EA] rounded-2xl w-full max-w-4xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-[#E5E5EA] flex items-center justify-between bg-[#FAFAFC]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[#FEF2F2] border border-[#FECACA] flex items-center justify-center text-[#DC2626]">
              <UploadCloud className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-[#1D1D1F]">
                YouTube Studio Staging & Launchpad
              </h2>
              <p className="text-xs text-[#86868B]">
                All metadata, tags, lyrics and assets pre-filled. Review, adjust, and push directly to YouTube.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleOpenStudio}
              className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-[#DC2626] to-[#B91C1C] hover:opacity-95 text-white text-xs font-bold rounded-xl transition-all shadow-sm cursor-pointer"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span>Open YouTube Studio</span>
            </button>
            <button
              onClick={onClose}
              className="p-2 text-[#86868B] hover:text-[#1D1D1F] hover:bg-[#E5E5EA] rounded-xl transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Scrollable Body */}
        <div className="p-6 overflow-y-auto space-y-5 flex-1">
          {/* Quick Guidance Alert */}
          <div className="bg-[#EFF6FF] border border-[#BFDBFE] rounded-xl p-3.5 flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-[#2563EB] shrink-0 mt-0.5" />
            <div className="text-xs text-[#1E40AF] space-y-1">
              <span className="font-bold block">100% Safe Creator Workflow</span>
              <p className="text-[11px] leading-relaxed text-[#1D4ED8]">
                Click <strong>"Open YouTube Studio"</strong> to launch studio.youtube.com. Your title is automatically copied to clipboard. Copy Description & Tags with 1 click below, or use Direct API Upload in Private mode.
              </p>
            </div>
          </div>

          {/* Media Assets Bar */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Final Video Card */}
            <div className="bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-[#F0FDF4] border border-[#BBF7D0] flex items-center justify-center text-[#16A34A]">
                  <Video className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-xs font-bold text-[#1D1D1F] block">Final Video (1080p MP4)</span>
                  <span className="text-[11px] text-[#86868B] block">Audio & 3D Visuals Synchronized</span>
                </div>
              </div>
              <a
                href={resolvedVideoUrl}
                download={`video_${projectId.slice(0, 8)}.mp4`}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-[#E5E5EA] hover:bg-[#F5F5F7] text-xs font-semibold text-[#1D1D1F] rounded-lg transition-colors cursor-pointer shadow-2xs"
              >
                <Download className="w-3.5 h-3.5 text-[#FF6B00]" />
                <span>Save Video</span>
              </a>
            </div>

            {/* Thumbnail Card */}
            <div className="bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-[#FAF5FF] border border-[#E9D5FF] flex items-center justify-center text-[#9333EA]">
                  <ImageIcon className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-xs font-bold text-[#1D1D1F] block">HD YouTube Thumbnail (16:9)</span>
                  <span className="text-[11px] text-[#86868B] block">High-CTR Toddler Palette</span>
                </div>
              </div>
              <a
                href={resolvedThumbUrl}
                download={`thumbnail_${projectId.slice(0, 8)}.jpg`}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-[#E5E5EA] hover:bg-[#F5F5F7] text-xs font-semibold text-[#1D1D1F] rounded-lg transition-colors cursor-pointer shadow-2xs"
              >
                <Download className="w-3.5 h-3.5 text-[#9333EA]" />
                <span>Save Thumbnail</span>
              </a>
            </div>
          </div>

          {/* 1. Title Input & Copy */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-[#DC2626]" />
                <span>Video Title (High-CTR / SEO Optimized)</span>
              </label>
              <button
                onClick={() => copyToClipboard(title, "title")}
                className="text-xs font-semibold text-[#DC2626] hover:text-[#B91C1C] flex items-center gap-1 cursor-pointer bg-[#FEF2F2] px-2.5 py-1 rounded-md border border-[#FECACA] transition-colors"
              >
                {copiedField === "title" ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-[#16A34A]" />
                    <span className="text-[#16A34A]">Copied Title!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy Title</span>
                  </>
                )}
              </button>
            </div>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full text-xs font-semibold text-[#1D1D1F] bg-white border border-[#E5E5EA] rounded-xl px-3.5 py-2.5 focus:outline-none focus:border-[#DC2626] transition-colors"
              placeholder="Catchy YouTube Title"
            />
            <span className="text-[10px] text-[#86868B] block">
              Character Count: {title.length} / 100 max recommended
            </span>
          </div>

          {/* 2. Description Input & Copy */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-[#FF6B00]" />
                <span>Full Description (Overview, Lyrics, Chapters & Hashtags)</span>
              </label>
              <button
                onClick={() => copyToClipboard(description, "description")}
                className="text-xs font-semibold text-[#DC2626] hover:text-[#B91C1C] flex items-center gap-1 cursor-pointer bg-[#FEF2F2] px-2.5 py-1 rounded-md border border-[#FECACA] transition-colors"
              >
                {copiedField === "description" ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-[#16A34A]" />
                    <span className="text-[#16A34A]">Copied Description!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy Description</span>
                  </>
                )}
              </button>
            </div>
            <textarea
              rows={7}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full text-xs text-[#1D1D1F] bg-white border border-[#E5E5EA] rounded-xl p-3.5 focus:outline-none focus:border-[#DC2626] font-mono leading-relaxed transition-colors"
              placeholder="YouTube description content with lyrics and hashtags"
            />
          </div>

          {/* 3. Tags & Hashtags Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Tags */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
                  <Tag className="w-3.5 h-3.5 text-[#2563EB]" />
                  <span>Video Tags (Comma-Separated)</span>
                </label>
                <button
                  onClick={() => copyToClipboard(tags, "tags")}
                  className="text-[11px] font-semibold text-[#2563EB] hover:text-[#1D4ED8] flex items-center gap-1 cursor-pointer bg-[#EFF6FF] px-2 py-0.5 rounded border border-[#BFDBFE]"
                >
                  {copiedField === "tags" ? <Check className="w-3 h-3 text-[#16A34A]" /> : <Copy className="w-3 h-3" />}
                  <span>{copiedField === "tags" ? "Copied!" : "Copy Tags"}</span>
                </button>
              </div>
              <textarea
                rows={3}
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                className="w-full text-xs text-[#1D1D1F] bg-white border border-[#E5E5EA] rounded-xl p-2.5 focus:outline-none focus:border-[#2563EB] font-mono text-[11px]"
                placeholder="nursery rhymes, kids songs, toddler cartoon..."
              />
            </div>

            {/* Hashtags */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
                  <Hash className="w-3.5 h-3.5 text-[#9333EA]" />
                  <span>Hashtags</span>
                </label>
                <button
                  onClick={() => copyToClipboard(hashtags, "hashtags")}
                  className="text-[11px] font-semibold text-[#9333EA] hover:text-[#7E22CE] flex items-center gap-1 cursor-pointer bg-[#FAF5FF] px-2 py-0.5 rounded border border-[#E9D5FF]"
                >
                  {copiedField === "hashtags" ? <Check className="w-3 h-3 text-[#16A34A]" /> : <Copy className="w-3 h-3" />}
                  <span>{copiedField === "hashtags" ? "Copied!" : "Copy Hashtags"}</span>
                </button>
              </div>
              <textarea
                rows={3}
                value={hashtags}
                onChange={(e) => setHashtags(e.target.value)}
                className="w-full text-xs text-[#1D1D1F] bg-white border border-[#E5E5EA] rounded-xl p-2.5 focus:outline-none focus:border-[#9333EA] font-mono text-[11px]"
                placeholder="#nurseryrhymes #kidssongs #cartoon"
              />
            </div>
          </div>

          {/* Mandatory YouTube Kids Flags */}
          <div className="bg-[#FFFBEB] border border-[#FDE68A] rounded-xl p-4 space-y-2">
            <span className="text-xs font-bold text-[#92400E] block">Required YouTube Studio Settings:</span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-[#78350F]">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#16A34A] shrink-0" />
                <span>Audience: <strong>Yes, it's made for kids</strong></span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#16A34A] shrink-0" />
                <span>Altered Content: <strong>Yes (AI Generated Animation)</strong></span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#16A34A] shrink-0" />
                <span>Category: <strong>Education (or Entertainment)</strong></span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#16A34A] shrink-0" />
                <span>Visibility: <strong>Private first</strong>, then Public after checks</span>
              </div>
            </div>
          </div>

          {/* API Upload Status / Feedback */}
          {apiResult && (
            <div
              className={`p-3.5 rounded-xl border text-xs flex items-center justify-between ${
                apiResult.success
                  ? "bg-[#F0FDF4] border-[#BBF7D0] text-[#166534]"
                  : "bg-[#FEF2F2] border-[#FECACA] text-[#991B1B]"
              }`}
            >
              <div className="flex items-center gap-2">
                {apiResult.success ? (
                  <CheckCircle2 className="w-4 h-4 text-[#16A34A] shrink-0" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-[#DC2626] shrink-0" />
                )}
                <span>{apiResult.message}</span>
              </div>
              {apiResult.url && (
                <a
                  href={apiResult.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-bold underline ml-2 shrink-0 flex items-center gap-1"
                >
                  <span>Open Video in Studio</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 border-t border-[#E5E5EA] bg-[#FAFAFC] flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="text-xs text-[#86868B]">
            {copiedField === "auto_title" ? (
              <span className="text-[#16A34A] font-semibold">Title copied to clipboard! Paste it into YouTube Studio.</span>
            ) : (
              <span>Edit any field above before uploading or copying.</span>
            )}
          </div>

          <div className="flex items-center gap-2.5 w-full sm:w-auto justify-end">
            <button
              onClick={handleDirectApiUpload}
              disabled={apiUploading}
              className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-semibold border border-[#E5E5EA] bg-white hover:bg-[#F5F5F7] text-[#1D1D1F] transition-all cursor-pointer disabled:opacity-50"
            >
              {apiUploading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Pushing to API...</span>
                </>
              ) : (
                <>
                  <UploadCloud className="w-3.5 h-3.5 text-[#2563EB]" />
                  <span>Direct API Upload (Private)</span>
                </>
              )}
            </button>

            <button
              onClick={handleOpenStudio}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold bg-[#DC2626] hover:bg-[#B91C1C] text-white transition-all shadow-sm cursor-pointer"
            >
              <ExternalLink className="w-4 h-4" />
              <span>Open YouTube Studio & Upload</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
