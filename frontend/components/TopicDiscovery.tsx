"use client";

import { useState, useEffect } from "react";
import { TopicOpportunity, Project } from "@/lib/types";
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
 SlidersHorizontal,
 Clock,
 Globe2,
 Baby,
 Hash,
 Layers,
 CheckCircle2,
 RotateCcw,
 ArrowDown,
} from "lucide-react";

interface TopicDiscoveryProps {
  onSelectTopic: (topic: TopicOpportunity) => void;
  activeTopic?: string;
  activeProjectId?: string;
  activeProject?: Project | null;
  existingProjects?: Project[];
  onSelectExistingProject?: (project: Project) => void;
}

function normalizeTopicString(str?: string): string {
  if (!str) return "";
  return str
    .toLowerCase()
    .replace(/[^a-z0-9]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function doesTopicMatchProject(t: TopicOpportunity, p?: Project | null): boolean {
  if (!p) return false;
  const tTopic = normalizeTopicString(t.topic);
  const tTitle = normalizeTopicString(t.suggested_title);
  const pTopic = normalizeTopicString(p.topic);
  const pTitle = normalizeTopicString(p.title);

  if (tTopic && pTopic && tTopic === pTopic) return true;
  if (tTitle && pTitle && tTitle === pTitle) return true;
  if (tTopic && pTitle && (pTitle.includes(tTopic) || tTopic.includes(pTopic))) return true;
  if (pTopic && tTitle && (tTitle.includes(pTopic) || pTopic.includes(tTitle))) return true;
  return false;
}

export function TopicDiscovery({
  onSelectTopic,
  activeTopic,
  activeProjectId,
  activeProject,
  existingProjects,
  onSelectExistingProject,
}: TopicDiscoveryProps) {
  const [loading, setLoading] = useState(false);
  const [topics, setTopics] = useState<TopicOpportunity[]>([]);
  const [activeModel, setActiveModel] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

 // Filters requested by user: age select, duration, language, limit
 const [targetAge, setTargetAge] = useState<string>("2–5 Years");
 const [duration, setDuration] = useState<string>("2–3 Minutes (Standard)");
 const [language, setLanguage] = useState<string>("English (US/UK)");
 const [suggestionsLimit, setSuggestionsLimit] = useState<number>(8);

 const fetchTopics = async (
 customLimit?: number,
 customAge?: string,
 customDur?: string,
 customLang?: string,
 customSeed?: number
 ) => {
 const limitToUse = customLimit !== undefined ? customLimit : suggestionsLimit;
 const ageToUse = customAge !== undefined ? customAge : targetAge;
 const durToUse = customDur !== undefined ? customDur : duration;
 const langToUse = customLang !== undefined ? customLang : language;
 const seedToUse = customSeed !== undefined ? customSeed : Date.now();

 setLoading(true);
 setErrorMessage(null);
 try {
 const data = await api.discoverTopics({
 limit: limitToUse,
 target_age: ageToUse,
 duration: durToUse,
 language: langToUse,
 seed: seedToUse,
 });
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

 // Automatically load initial topics on page load
 fetchTopics(8, "2–5 Years", "2–3 Minutes (Standard)", "English (US/UK)", 1001);
 }, []);

 return (
 <div className="space-y-5">
 {/* Top Banner Card */}
 <div className="bg-gradient-to-r from-orange-500/10 via-amber-500/5 to-transparent border border-orange-200/60 rounded-3xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
 <div className="space-y-1 max-w-xl">
 <div className="flex flex-wrap items-center gap-2">
 <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-orange-100 text-orange-800 border border-orange-200">
 <Flame className="w-3.5 h-3.5 text-orange-600 fill-orange-500" />
 <span>Step 1 • 100% Dynamic AI Topic Discovery</span>
 </div>
 <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
 <span> Zero Repeats • Produced Topics Excluded</span>
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
 Live AI evaluates search intent, preschool trends, and audio-visual opportunity signals to generate fresh, unique candidates with 10M+ view potential without repeating past video topics.
 </p>
 </div>

 <button
 onClick={() => fetchTopics(suggestionsLimit, targetAge, duration, language, Date.now())}
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
 <span> Generate Fresh Rhyme Topics (Million-View Potential)</span>
 </>
 )}
 </button>
 </div>

 {/* FILTER BAR: Target Age, Duration, Language, and Limit */}
 <div className="bg-white border border-[#E5E5EA] rounded-2xl p-4 shadow-xs space-y-3">
 <div className="flex items-center justify-between border-b border-[#F0F0F2] pb-2.5">
 <div className="flex items-center gap-2 text-xs font-bold text-[#1D1D1F]">
 <SlidersHorizontal className="w-4 h-4 text-[#FF6B00]" />
 <span>AI Discovery Filters & Targeting</span>
 </div>
 <span className="text-[11px] text-[#86868B]">
 Filters adjust prompts and update topics in real-time
 </span>
 </div>

 <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
 {/* 1. Age Select */}
 <div className="space-y-1.5">
 <label className="text-[11px] font-bold text-[#1D1D1F] flex items-center gap-1.5">
 <Baby className="w-3.5 h-3.5 text-[#FF6B00]" />
 <span>Target Age Group</span>
 </label>
 <select
 value={targetAge}
 onChange={(e) => {
 const val = e.target.value;
 setTargetAge(val);
 fetchTopics(suggestionsLimit, val, duration, language, Date.now());
 }}
 className="w-full bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl px-3 py-2 text-xs text-[#1D1D1F] font-medium focus:outline-none focus:border-[#FF6B00] cursor-pointer"
 >
 <option value="All Ages (1–6 Years)">All Ages (1–6 Years)</option>
 <option value="1–3 Years (Toddlers)">1–3 Years (Toddlers & Babies)</option>
 <option value="2–5 Years (Preschool)">2–5 Years (Preschool Standard)</option>
 <option value="4–6 Years (Kindergarten)">4–6 Years (Kindergarten & Prep)</option>
 </select>
 </div>

 {/* 2. Duration Select */}
 <div className="space-y-1.5">
 <label className="text-[11px] font-bold text-[#1D1D1F] flex items-center gap-1.5">
 <Clock className="w-3.5 h-3.5 text-blue-600" />
 <span>Song / Video Duration</span>
 </label>
 <select
 value={duration}
 onChange={(e) => {
 const val = e.target.value;
 setDuration(val);
 fetchTopics(suggestionsLimit, targetAge, val, language, Date.now());
 }}
 className="w-full bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl px-3 py-2 text-xs text-[#1D1D1F] font-medium focus:outline-none focus:border-blue-500 cursor-pointer"
 >
 <option value="1–2 Minutes (Short & Viral)">1–2 Min (Short & Viral Hook)</option>
 <option value="2–3 Minutes (Standard)">2–3 Min (Standard Nursery Rhyme)</option>
 <option value="3–5 Minutes (Extended)">3–5 Min (Extended Bedtime/Lullaby)</option>
 </select>
 </div>

 {/* 3. Language Select */}
 <div className="space-y-1.5">
 <label className="text-[11px] font-bold text-[#1D1D1F] flex items-center gap-1.5">
 <Globe2 className="w-3.5 h-3.5 text-emerald-600" />
 <span>Target Language & Market</span>
 </label>
 <select
 value={language}
 onChange={(e) => {
 const val = e.target.value;
 setLanguage(val);
 fetchTopics(suggestionsLimit, targetAge, duration, val, Date.now());
 }}
 className="w-full bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl px-3 py-2 text-xs text-[#1D1D1F] font-medium focus:outline-none focus:border-emerald-500 cursor-pointer"
 >
 <option value="English (US/UK)">English (US/UK Global)</option>
 <option value="Hindi / Hinglish">Hindi / Hinglish (चंदा मामा / Kids Rhymes)</option>
 <option value="Spanish (Español)">Spanish (Canciones Infantiles)</option>
 <option value="Bilingual (English + Hindi)">Bilingual (English + Hindi)</option>
 <option value="Bilingual (English + Spanish)">Bilingual (English + Spanish)</option>
 </select>
 </div>

 {/* 4. Suggestions Limit */}
 <div className="space-y-1.5">
 <label className="text-[11px] font-bold text-[#1D1D1F] flex items-center gap-1.5">
 <Hash className="w-3.5 h-3.5 text-purple-600" />
 <span>Suggestions Limit</span>
 </label>
 <select
 value={suggestionsLimit}
 onChange={(e) => {
 const val = Number(e.target.value);
 setSuggestionsLimit(val);
 fetchTopics(val, targetAge, duration, language, Date.now());
 }}
 className="w-full bg-[#FAFAFC] border border-[#E5E5EA] rounded-xl px-3 py-2 text-xs text-[#1D1D1F] font-medium focus:outline-none focus:border-purple-500 cursor-pointer"
 >
 <option value={4}>4 Candidates (Fastest)</option>
 <option value={6}>6 Candidates (Balanced)</option>
 <option value={8}>8 Candidates (Recommended)</option>
 <option value={12}>12 Candidates (Wide Variety)</option>
 </select>
 </div>
 </div>
 </div>

 {errorMessage && (
 <div className="p-4 bg-red-50 border border-red-200 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-red-800">
 <div className="flex items-center gap-2">
 <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
 <span>{errorMessage}</span>
 </div>
 <div className="flex items-center gap-2 shrink-0">
 <button
 onClick={() => fetchTopics(suggestionsLimit, targetAge, duration, language, Date.now())}
 className="px-3 py-1.5 bg-red-600 text-white font-bold rounded-xl hover:bg-red-700 flex items-center gap-1 cursor-pointer"
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

 {/* Topics Header & Counter */}
 {topics.length > 0 && (
 <div className="flex items-center justify-between px-1 pt-1">
 <div className="flex items-center gap-2">
 <span className="text-xs font-bold text-[#1D1D1F]">
 Discovered Topic Opportunities
 </span>
 <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-orange-100 text-orange-800 border border-orange-200">
 {topics.length} Candidates Available
 </span>
 </div>
 <button
 onClick={() => fetchTopics(suggestionsLimit, targetAge, duration, language, Date.now())}
 disabled={loading}
 className="text-[11px] font-bold text-[#FF6B00] hover:underline flex items-center gap-1 cursor-pointer"
 >
 <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
 <span>Shuffle Topics</span>
 </button>
 </div>
 )}

 {existingProjects && existingProjects.length > 0 && (
 <div className="bg-white border border-[#E5E5EA] rounded-2xl p-4 shadow-xs space-y-3">
 <div className="flex items-center justify-between">
 <span className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
 <Layers className="w-3.5 h-3.5 text-[#FF6B00]" />
 <span>Ongoing Studio Productions ({existingProjects.length})</span>
 </span>
 <span className="text-[11px] text-[#86868B]">Click any ongoing project to instantly restore its flow</span>
 </div>
 <div className="flex items-center gap-2 overflow-x-auto pb-1 select-none">
 {existingProjects.map((p) => {
 const isActive = activeProjectId ? p.id === activeProjectId : activeProject?.id === p.id;
 return (
 <button
 key={p.id}
 onClick={() => {
 if (onSelectExistingProject) {
 onSelectExistingProject(p);
 } else {
 onSelectTopic({
 topic: p.topic,
 suggested_title: p.title,
 category: p.video_type || "Nursery Rhyme",
 target_age: p.target_age || "2-5 Years",
 duration: `${p.duration_min}-${p.duration_max} Minutes`,
 search_keywords: [],
 content_angle: p.topic,
 why_worth_considering: "Ongoing project in studio",
 opportunity_signals: "Previously created",
 suggested_characters: [],
 suggested_story_concept: p.title || p.topic,
 });
 }
 }}
 className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all cursor-pointer border ${
 isActive
 ? "bg-emerald-50 border-emerald-500 text-emerald-800 font-bold shadow-xs ring-2 ring-emerald-500/20"
 : "bg-[#FAFAFC] hover:bg-[#F5F5F7] text-[#1D1D1F] border-[#E5E5EA]"
 }`}
 >
 <span className={`w-2 h-2 rounded-full ${isActive ? "bg-emerald-500 animate-pulse" : "bg-slate-300"}`} />
 <span className="max-w-[180px] truncate">{p.title || p.topic}</span>
 <span className="text-[10px] px-1.5 py-0.5 rounded bg-white border border-[#E5E5EA] text-[#6E6E73] font-mono">
 {isActive ? "Active Now" : p.status}
 </span>
 </button>
 );
 })}
 </div>

 {/* Highlight Active Flow Banner */}
 {activeProject && (
 <div className="bg-gradient-to-r from-emerald-50/90 to-teal-50/70 border border-emerald-300 rounded-xl p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 shadow-2xs">
 <div className="flex items-center gap-2.5 min-w-0">
 <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shrink-0" />
 <div className="min-w-0">
 <div className="flex items-center gap-2">
 <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-900 bg-emerald-100 border border-emerald-200 px-2 py-0.5 rounded">
 Active Studio Production Flow
 </span>
 <span className="text-[11px] font-mono text-emerald-800 font-bold">
 {activeProject.status}
 </span>
 </div>
 <p className="text-xs font-bold text-[#1D1D1F] truncate mt-0.5">
 {activeProject.title || activeProject.topic}
 </p>
 </div>
 </div>
 <button
 onClick={() => {
 const el = document.getElementById("step-2-section");
 if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
 }}
 className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-lg transition-all flex items-center gap-1.5 shrink-0 cursor-pointer shadow-xs"
 >
 <span>Scroll to Flow (Steps 2–10)</span>
 <ArrowRight className="w-3.5 h-3.5" />
 </button>
 </div>
 )}
 </div>
 )}

 {topics.length > 0 && (() => {
 const activeTopicCardIndex = topics.findIndex((t) => {
 if (activeProjectId || activeProject) {
 const targetId = activeProjectId || activeProject?.id;
 const matched = existingProjects?.find((p) => doesTopicMatchProject(t, p));
 if (matched && matched.id === targetId) return true;
 if (activeProject && doesTopicMatchProject(t, activeProject) && activeProject.id === targetId) return true;
 return false;
 }
 if (activeTopic) {
 const normActive = normalizeTopicString(activeTopic);
 const tTop = normalizeTopicString(t.topic);
 const tTit = normalizeTopicString(t.suggested_title);
 return (tTop && (normActive === tTop || normActive.includes(tTop) || tTop.includes(normActive))) ||
 (tTit && (normActive === tTit || normActive.includes(tTit) || tTit.includes(normActive)));
 }
 return false;
 });

 return (
 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
 {topics.map((t, idx) => {
 const isSelected = (idx === activeTopicCardIndex);
 const existingProj = existingProjects?.find((p) => doesTopicMatchProject(t, p));

 return (
 <div
 key={idx}
 className={`bg-white border rounded-2xl p-4.5 shadow-xs flex flex-col justify-between space-y-3.5 transition-all hover:shadow-md ${
 isSelected
 ? "border-emerald-500 ring-2 ring-emerald-500/25 bg-emerald-50/10 shadow-sm shadow-emerald-500/5"
 : existingProj
 ? "border-blue-200 hover:border-blue-300"
 : "border-[#E5E5EA] hover:border-orange-300"
 }`}
 >
 <div className="space-y-2.5">
 <div className="flex items-center justify-between gap-2">
 {isSelected ? (
 <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1.5 shadow-2xs">
 <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
 Active Production
 </span>
 ) : existingProj ? (
 <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
 Saved • {existingProj.status}
 </span>
 ) : (
 <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-orange-50 text-[#C2410C] border border-orange-100 truncate">
 {t.category}
 </span>
 )}
 <span className="text-[10px] font-semibold text-[#86868B] shrink-0">
 Age: {t.target_age}
 </span>
 </div>

 <div>
 <h3 className="text-sm font-bold text-[#1D1D1F] line-clamp-2">
 {t.suggested_title}
 </h3>
 <p className="text-[11px] text-[#6E6E73] mt-1 line-clamp-2">
 {t.content_angle}
 </p>
 </div>

 <div className="p-2.5 bg-[#FAFAFC] rounded-xl border border-[#EDEDF0] space-y-1.5 text-[11px]">
 <div className="text-[#1D1D1F]">
 <span className="font-bold text-[#C2410C]">Why consider: </span>
 <span className="text-[#6E6E73]">{t.why_worth_considering}</span>
 </div>
 {t.opportunity_signals && (
 <div className="flex items-start gap-1 text-[#059669] font-medium">
 <TrendingUp className="w-3 h-3 shrink-0 mt-0.5" />
 <span className="text-[10px] line-clamp-1">{t.opportunity_signals}</span>
 </div>
 )}
 </div>

 {t.suggested_characters && t.suggested_characters.length > 0 && (
 <div className="flex items-center gap-1.5 text-[10px] text-[#86868B]">
 <Users2 className="w-3 h-3 text-[#FF6B00] shrink-0" />
 <span className="truncate">{t.suggested_characters.join(", ")}</span>
 </div>
 )}

 {/* SEO & High-CPM Tags */}
 {(t.seo_tags || t.search_keywords) && (
 <div className="flex flex-wrap gap-1 pt-1">
 {(t.seo_tags || t.search_keywords.slice(0, 3)).slice(0, 3).map((tag, sIdx) => (
 <span
 key={sIdx}
 className="text-[9px] font-bold px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 border border-blue-100 truncate max-w-[120px]"
 >
 {tag.startsWith("#") ? tag : `#${tag.replace(/\s+/g, "")}`}
 </span>
 ))}
 </div>
 )}
 </div>

 {isSelected ? (
 <button
 onClick={() => {
 const el = document.getElementById("step-2-section");
 if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
 }}
 className="w-full text-xs font-bold py-2.5 px-3.5 rounded-xl transition-all flex items-center justify-between cursor-pointer bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white shadow-sm shadow-emerald-600/20 group border border-emerald-500/80"
 >
 <div className="flex items-center gap-2">
 <span className="flex h-2 w-2 relative">
 <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-200 opacity-75" />
 <span className="relative inline-flex rounded-full h-2 w-2 bg-white" />
 </span>
 <span className="tracking-wide">Active Production</span>
 </div>
 <div className="flex items-center gap-1 text-[11px] font-semibold text-emerald-100 group-hover:text-white transition-colors bg-white/15 px-2 py-0.5 rounded-md">
 <span>View Flow</span>
 <ArrowDown className="w-3.5 h-3.5 group-hover:translate-y-0.5 transition-transform" />
 </div>
 </button>
 ) : existingProj ? (
 <button
 onClick={() => {
 if (onSelectExistingProject) {
 onSelectExistingProject(existingProj);
 } else {
 onSelectTopic(t);
 }
 }}
 className="w-full text-xs font-bold py-2.5 px-3.5 rounded-xl border transition-all flex items-center justify-between cursor-pointer bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-200 shadow-2xs group"
 >
 <div className="flex items-center gap-1.5">
 <RotateCcw className="w-3.5 h-3.5 text-blue-600 group-hover:-rotate-45 transition-transform" />
 <span>Switch & Restore Flow</span>
 </div>
 <span className="text-[10px] font-mono text-blue-600/80 bg-blue-100/60 px-1.5 py-0.5 rounded">
 {existingProj.status}
 </span>
 </button>
 ) : (
 <button
 onClick={() => {
 onSelectTopic(t);
 }}
 className="w-full text-xs font-bold py-2.5 px-3.5 rounded-xl border transition-all flex items-center justify-between cursor-pointer bg-[#FAFAFC] text-[#1D1D1F] border-[#E5E5EA] hover:bg-orange-50 hover:text-[#FF6B00] hover:border-orange-200 group"
 >
 <span>Select Topic & Start Flow</span>
 <ArrowRight className="w-3.5 h-3.5 text-[#86868B] group-hover:text-[#FF6B00] group-hover:translate-x-0.5 transition-all" />
 </button>
 )}
 </div>
 );
 })}
 </div>
 );
 })()}
 </div>
 );
}

export default TopicDiscovery;
