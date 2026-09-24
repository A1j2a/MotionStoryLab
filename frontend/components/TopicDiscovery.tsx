"use client";

import { useState, useEffect } from "react";
import { TopicOpportunity } from "@/lib/types";
import { api } from "@/lib/api";
import Link from "next/link";
import {
  Flame,
  ArrowRight,
  Users2,
  TrendingUp,
  Loader2,
  Cpu,
  AlertCircle,
  RefreshCw,
  Settings,
} from "lucide-react";

interface TopicDiscoveryProps {
  onSelectTopic: (topic: TopicOpportunity) => void;
}

export function TopicDiscovery({ onSelectTopic }: TopicDiscoveryProps) {
  const [loading, setLoading] = useState(false);
  const [topics, setTopics] = useState<TopicOpportunity[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<TopicOpportunity | null>(null);
  const [activeModel, setActiveModel] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    api.getAISettings()
      .then((s) => {
        if (s.openrouter_enabled && s.openrouter_model) {
          setActiveModel(s.openrouter_model);
        } else {
          setActiveModel(s.active_provider || "Local Ollama");
        }
      })
      .catch(() => {});
  }, []);

  const fetchTopics = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const data = await api.discoverTopics(8);
      if (Array.isArray(data) && data.length > 0) {
        setTopics(data);
      } else {
        setErrorMessage("AI model returned no topics. Please check your AI model settings or retry.");
      }
    } catch (err: any) {
      console.error("Failed to discover topics:", err);
      const msg = err?.message || "Failed to generate topics via AI model.";
      setErrorMessage(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-orange-500/10 via-amber-500/5 to-transparent border border-orange-200/60 rounded-3xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1 max-w-xl">
          <div className="flex flex-wrap items-center gap-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-orange-100 text-orange-800 border border-orange-200">
              <Flame className="w-3.5 h-3.5 text-orange-600 fill-orange-500" />
              <span>Step 1 • 100% Dynamic AI Topic Discovery</span>
            </div>
            {activeModel && (
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-50 text-purple-700 border border-purple-200">
                <Cpu className="w-3 h-3 text-purple-600" />
                <span>AI Engine: {activeModel.split("/").pop() || activeModel}</span>
              </div>
            )}
          </div>
          <h2 className="text-xl font-bold text-[#1D1D1F]">
            Find Today&apos;s High-Engagement Kids & Nursery Rhyme Topics
          </h2>
          <p className="text-xs text-[#6E6E73] leading-relaxed">
            Live AI evaluates search intent, preschool trends, and audio-visual opportunity signals to generate structured candidates in real-time.
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
              <span>AI Researching Fresh Topics...</span>
            </>
          ) : (
            <>
              <Flame className="w-4 h-4 fill-white" />
              <span>🔥 Find Today&apos;s Kids Topics</span>
            </>
          )}
        </button>
      </div>

      {errorMessage && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-red-800">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={fetchTopics}
              className="px-3 py-1.5 bg-red-600 text-white font-bold rounded-xl hover:bg-red-700 flex items-center gap-1"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Retry</span>
            </button>
            <Link
              href="/settings"
              className="px-3 py-1.5 bg-white text-red-700 border border-red-300 font-bold rounded-xl hover:bg-red-50 flex items-center gap-1"
            >
              <Settings className="w-3 h-3" />
              <span>Settings</span>
            </Link>
          </div>
        </div>
      )}

      {topics.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {topics.map((t, idx) => {
            const isSelected = selectedTopic?.topic === t.topic;
            return (
              <div
                key={idx}
                className={`bg-white border rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-4 transition-all hover:shadow-md ${
                  isSelected
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
            );
          })}
        </div>
      )}
    </div>
  );
}
