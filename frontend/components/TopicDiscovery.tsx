"use client";

import { useState } from "react";
import { TopicOpportunity } from "@/lib/types";
import { api } from "@/lib/api";
import {
  Flame,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Users2,
  Tag,
  Search,
  BookOpen,
  TrendingUp,
  Loader2,
} from "lucide-react";

interface TopicDiscoveryProps {
  onSelectTopic: (topic: TopicOpportunity) => void;
}

export function TopicDiscovery({ onSelectTopic }: TopicDiscoveryProps) {
  const [loading, setLoading] = useState(false);
  const [topics, setTopics] = useState<TopicOpportunity[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<TopicOpportunity | null>(null);

  const fetchTopics = async () => {
    setLoading(true);
    try {
      const data = await api.discoverTopics(12);
      setTopics(data);
    } catch (err) {
      console.error("Failed to discover topics:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-orange-500/10 via-amber-500/5 to-transparent border border-orange-200/60 rounded-3xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1 max-w-xl">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-orange-100 text-orange-800 border border-orange-200">
            <Flame className="w-3.5 h-3.5 text-orange-600 fill-orange-500" />
            <span>Step 1 • Topic Discovery & Opportunity Research</span>
          </div>
          <h2 className="text-xl font-bold text-[#1D1D1F]">
            Find Today&apos;s High-Engagement Kids & Nursery Rhyme Topics
          </h2>
          <p className="text-xs text-[#6E6E73] leading-relaxed">
            AI evaluates search intent, preschool trends, and audio-visual opportunity signals to generate 10–15 structured candidates.
          </p>
        </div>

        <button
          onClick={fetchTopics}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 bg-gradient-to-r from-[#FF6B00] to-[#EA580C] hover:opacity-95 text-white text-xs font-bold px-6 py-3.5 rounded-2xl shadow-md shadow-orange-500/20 transition-all cursor-pointer whitespace-nowrap disabled:opacity-50"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Researching Topics...</span>
            </>
          ) : (
            <>
              <Flame className="w-4 h-4 fill-white" />
              <span>🔥 Find Today&apos;s Kids Topics</span>
            </>
          )}
        </button>
      </div>

      {topics.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {topics.map((t, idx) => (
            <div
              key={idx}
              className={`bg-white border rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-4 transition-all hover:shadow-md ${
                selectedTopic?.topic === t.topic
                  ? "border-[#FF6B00] ring-2 ring-orange-500/20"
                  : "border-[#E5E5EA] hover:border-orange-300"
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-orange-50 text-[#C2410C] border border-orange-100">
                    {t.category}
                  </span>
                  <span className="text-[11px] font-semibold text-[#86868B]">
                    Age: {t.target_age}
                  </span>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-[#1D1D1F] line-clamp-2">
                    {t.suggested_title}
                  </h3>
                  <p className="text-[11px] text-[#6E6E73] mt-1 line-clamp-2">
                    {t.story_concept || t.suggested_story_concept}
                  </p>
                </div>

                <div className="p-3 bg-[#FAFAFC] rounded-xl border border-[#F0F0F2] space-y-2 text-[11px]">
                  <div className="text-[#1D1D1F]">
                    <strong className="text-[#FF6B00]">Why consider: </strong>
                    <span className="text-[#6E6E73]">{t.why_worth_considering}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-[#6E6E73] pt-1 border-t border-[#EDEDF0]">
                    <TrendingUp className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span className="text-[10px] truncate">{t.opportunity_signals}</span>
                  </div>
                </div>

                {t.suggested_characters && t.suggested_characters.length > 0 && (
                  <div className="flex items-center gap-1.5 text-[11px] text-[#6E6E73]">
                    <Users2 className="w-3.5 h-3.5 text-[#86868B] shrink-0" />
                    <span className="truncate">
                      {t.suggested_characters.join(", ")}
                    </span>
                  </div>
                )}
              </div>

              <button
                onClick={() => {
                  setSelectedTopic(t);
                  onSelectTopic(t);
                }}
                className="w-full inline-flex items-center justify-center gap-2 bg-[#FAFAFC] hover:bg-orange-500 hover:text-white text-[#1D1D1F] border border-[#E5E5EA] hover:border-orange-500 text-xs font-bold py-2.5 rounded-xl transition-all cursor-pointer"
              >
                <span>Select Topic</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
