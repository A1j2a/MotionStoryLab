"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { HealthData, AISettings, TestConnectionResult, ServiceToolItem } from "@/lib/types";
import {
  Settings as SettingsIcon,
  CheckCircle2,
  XCircle,
  HardDrive,
  RefreshCw,
  Cpu,
  Server,
  Trash2,
  AlertTriangle,
  FolderArchive,
  Database,
  ShieldCheck,
  Sparkles,
  Key,
  Eye,
  EyeOff,
  Zap,
  Check,
  ExternalLink,
  Bot,
  BrainCircuit,
  Sliders,
  Power,
  PowerOff,
  Activity,
  Copy,
  Music,
  Radio,
  UploadCloud,
  Video,
  Film,
  Image as ImageIcon,
  Monitor,
  Smartphone,
  Clapperboard,
} from "lucide-react";

export default function SettingsPage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [services, setServices] = useState<ServiceToolItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [storage, setStorage] = useState<{
    total_formatted: string;
    projects_formatted: string;
    logs_formatted: string;
    project_count: number;
    project_dir: string;
  } | null>(null);
  const [cleaning, setCleaning] = useState(false);

  // OpenRouter & AI Settings State
  const [aiSettings, setAiSettings] = useState<AISettings | null>(null);
  const [enabled, setEnabled] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [showApiKey, setShowApiKey] = useState(false);
  const [selectedModel, setSelectedModel] = useState("meta-llama/llama-3.3-70b-instruct");
  const [customModel, setCustomModel] = useState("");
  const [savingAI, setSavingAI] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [copiedKey, setCopiedKey] = useState(false);

  // Video Settings State
  // Wan & AI Provider Settings State
  const [videoProvider, setVideoProvider] = useState("wan");
  const [useWanVideo, setUseWanVideo] = useState(false);
  const [useAiThumbnail, setUseAiThumbnail] = useState(false);
  const [useAiReferenceImages, setUseAiReferenceImages] = useState(false);
  const [aiProviderTestMode, setAiProviderTestMode] = useState(false);
  const [falKey, setFalKey] = useState("");
  const [showFalKey, setShowFalKey] = useState(false);
  const [wanModel, setWanModel] = useState("fal-ai/wan-flf2v");
  const [wanResolution, setWanResolution] = useState("720p");
  const [wanTestMode, setWanTestMode] = useState(false);
  const [videoAspectRatio, setVideoAspectRatio] = useState("16:9");
  const [falKeySaved, setFalKeySaved] = useState(false);

  // Thumbnail Settings State
  const [thumbEnabled, setThumbEnabled] = useState(true);
  const [thumbModel, setThumbModel] = useState("high_ctr_graphic");
  const [thumbAspectRatio, setThumbAspectRatio] = useState("16:9");
  const [autoSongEnabled, setAutoSongEnabled] = useState(true);
  const [testingThumb, setTestingThumb] = useState(false);
  const [thumbTestResult, setThumbTestResult] = useState<any | null>(null);
  const [thumbTestError, setThumbTestError] = useState<string | null>(null);

  // Text Model Testing State
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<TestConnectionResult | null>(null);
  const [testError, setTestError] = useState<string | null>(null);

  // Service toggle state
  const [serviceActionLoading, setServiceActionLoading] = useState<string | null>(null);
  const [optimizeMessage, setOptimizeMessage] = useState<string | null>(null);

  const fetchHealth = async () => {
    setLoading(true);
    try {
      const data = await api.getHealth();
      setHealth(data);
    } catch {
      // offline
    } finally {
      setLoading(false);
    }
  };

  const fetchServices = async () => {
    try {
      const data = await api.getServicesStatus();
      if (data && data.services) {
        setServices(data.services);
      }
    } catch (err) {
      console.error("Failed to load service list:", err);
    }
  };

  const fetchStorage = async () => {
    try {
      const data = await api.getStorageStatus();
      setStorage(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchAISettings = async () => {
    try {
      const data = await api.getAISettings();
      setAiSettings(data);
      setEnabled(data.openrouter_enabled);
      setSelectedModel(data.openrouter_model || "meta-llama/llama-3.3-70b-instruct");
      if (data.openrouter_api_key) {
        setApiKey(data.openrouter_api_key);
      }
      setVideoProvider(data.video_provider || "wan");
      setUseWanVideo(data.use_wan_video !== undefined ? data.use_wan_video : (data.video_provider === "wan"));
      setUseAiThumbnail(data.use_ai_thumbnail !== undefined ? data.use_ai_thumbnail : false);
      setUseAiReferenceImages(data.use_ai_reference_images !== undefined ? data.use_ai_reference_images : false);
      setAiProviderTestMode(data.ai_provider_test_mode !== undefined ? data.ai_provider_test_mode : (data.wan_test_mode || false));
      if (data.fal_key_masked) {
        setFalKey(data.fal_key_masked);
      }
      setWanModel(data.wan_model || "fal-ai/wan-flf2v");
      setWanResolution(data.wan_resolution || "720p");
      setWanTestMode(data.wan_test_mode || false);
      setVideoAspectRatio(data.video_aspect_ratio || "16:9");
      setThumbEnabled(data.thumbnail_generator_enabled !== undefined ? data.thumbnail_generator_enabled : true);
      setThumbModel(data.thumbnail_model || "high_ctr_graphic");
      setThumbAspectRatio(data.thumbnail_aspect_ratio || "16:9");
      setAutoSongEnabled(data.auto_song_generation_enabled !== false);
    } catch (err) {
      console.error("Failed to load AI settings:", err);
    }
  };

  useEffect(() => {
    fetchHealth();
    fetchServices();
    fetchStorage();
    fetchAISettings();
    const interval = setInterval(() => {
      fetchHealth();
      fetchServices();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSaveAISettings = async (
    overrideEnabled?: boolean,
    overrideThumbEnabled?: boolean,
    overrideAutoSong?: boolean,
    overrideVideoProvider?: string,
    overrideWanVideo?: boolean,
    overrideAiThumb?: boolean,
    overrideAiRef?: boolean,
    overrideTestMode?: boolean
  ) => {
    setSavingAI(true);
    setSaveSuccess(false);
    setTestResult(null);
    setTestError(null);

    const isEnabled = overrideEnabled !== undefined ? overrideEnabled : enabled;
    const isThumbEnabled = overrideThumbEnabled !== undefined ? overrideThumbEnabled : thumbEnabled;
    const isAutoSongEnabled = overrideAutoSong !== undefined ? overrideAutoSong : autoSongEnabled;
    const isVideoProvider = overrideVideoProvider !== undefined ? overrideVideoProvider : videoProvider;
    const isWanVideo = overrideWanVideo !== undefined ? overrideWanVideo : (useWanVideo || isVideoProvider === "wan");
    const isAiThumb = overrideAiThumb !== undefined ? overrideAiThumb : useAiThumbnail;
    const isAiRef = overrideAiRef !== undefined ? overrideAiRef : useAiReferenceImages;
    const isTestMode = overrideTestMode !== undefined ? overrideTestMode : (aiProviderTestMode || wanTestMode);
    const modelToSave = customModel.trim() ? customModel.trim() : selectedModel;

    try {
      const updated = await api.updateAISettings({
        openrouter_enabled: isEnabled,
        openrouter_api_key: apiKey.trim() ? apiKey.trim() : undefined,
        openrouter_model: modelToSave,
        video_provider: isVideoProvider,
        use_wan_video: isWanVideo,
        use_ai_thumbnail: isAiThumb,
        use_ai_reference_images: isAiRef,
        ai_provider_test_mode: isTestMode,
        fal_key: falKey.trim() && !falKey.includes("***") ? falKey.trim() : undefined,
        wan_model: wanModel,
        wan_resolution: wanResolution,
        wan_test_mode: isTestMode,
        video_aspect_ratio: videoAspectRatio,
        thumbnail_generator_enabled: isThumbEnabled,
        thumbnail_model: thumbModel,
        thumbnail_aspect_ratio: thumbAspectRatio,
        auto_song_generation_enabled: isAutoSongEnabled,
      });
      setAiSettings(updated);
      setEnabled(updated.openrouter_enabled);
      setVideoProvider(updated.video_provider || "wan");
      setUseWanVideo(updated.use_wan_video !== undefined ? updated.use_wan_video : (updated.video_provider === "wan"));
      setUseAiThumbnail(updated.use_ai_thumbnail || false);
      setUseAiReferenceImages(updated.use_ai_reference_images || false);
      setAiProviderTestMode(updated.ai_provider_test_mode || updated.wan_test_mode || false);
      if (updated.fal_key_masked) {
        setFalKey(updated.fal_key_masked);
      }
      setWanModel(updated.wan_model || "fal-ai/wan-flf2v");
      setWanResolution(updated.wan_resolution || "720p");
      setWanTestMode(updated.wan_test_mode || false);
      setThumbEnabled(updated.thumbnail_generator_enabled);
      setAutoSongEnabled(updated.auto_song_generation_enabled !== false);
      if (updated.openrouter_api_key) {
        setApiKey(updated.openrouter_api_key);
      }
      setSaveSuccess(true);
      setFalKeySaved(true);
      setTimeout(() => {
        setSaveSuccess(false);
        setFalKeySaved(false);
      }, 3000);
    } catch (err: any) {
      alert("Failed to save AI settings: " + err.message);
    } finally {
      setSavingAI(false);
    }
  };

  const handleToggleOpenRouter = async () => {
    const nextState = !enabled;
    setEnabled(nextState);
    await handleSaveAISettings(nextState, thumbEnabled, autoSongEnabled);
  };

  const handleToggleAutoSong = async () => {
    const nextState = !autoSongEnabled;
    setAutoSongEnabled(nextState);
    await handleSaveAISettings(enabled, thumbEnabled, nextState);
  };

  const handleToggleThumbnail = async () => {
    const nextState = !thumbEnabled;
    setThumbEnabled(nextState);
    await handleSaveAISettings(enabled, nextState, autoSongEnabled);
  };

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);
    setTestError(null);

    const modelToTest = customModel.trim() ? customModel.trim() : selectedModel;

    try {
      const res = await api.testOpenRouterConnection({
        api_key: apiKey.trim() ? apiKey.trim() : undefined,
        model: modelToTest,
      });
      setTestResult(res);
    } catch (err: any) {
      setTestError(err.message || "Connection failed.");
    } finally {
      setTesting(false);
    }
  };

  const handleTestThumbnail = async () => {
    setTestingThumb(true);
    setThumbTestResult(null);
    setThumbTestError(null);

    try {
      const res = await api.testThumbnailConnection({
        title: "Numbers Farm: 1 to 10 Fun!",
        topic: "Preschool Rhyme",
        model: thumbModel,
        aspect_ratio: thumbAspectRatio,
      });
      setThumbTestResult(res);
    } catch (err: any) {
      setThumbTestError(err.message || "Thumbnail test failed.");
    } finally {
      setTestingThumb(false);
    }
  };

  const handleCopyKey = () => {
    if (!apiKey) return;
    navigator.clipboard.writeText(apiKey);
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 2000);
  };

  const handleToggleService = async (serviceKey: string, currentlyRunning: boolean) => {
    setServiceActionLoading(serviceKey);
    try {
      if (currentlyRunning) {
        await api.stopService(serviceKey);
      } else {
        await api.startService(serviceKey);
      }
      await fetchServices();
      await fetchHealth();
    } catch (err: any) {
      alert("Service action failed: " + err.message);
    } finally {
      setServiceActionLoading(null);
    }
  };

  const handleStopUnused = async () => {
    setServiceActionLoading("optimize");
    try {
      const res = await api.stopUnusedServices();
      setOptimizeMessage(res.message);
      await fetchServices();
      await fetchHealth();
      setTimeout(() => setOptimizeMessage(null), 5000);
    } catch (err: any) {
      alert("Optimize failed: " + err.message);
    } finally {
      setServiceActionLoading(null);
    }
  };

  const handleClearCache = async (purgeAll: boolean) => {
    const confirmMsg = purgeAll
      ? "Are you sure you want to PURGE ALL projects and reset studio storage? This cannot be undone."
      : "Clean temporary scene frames and cache? Final rendered videos and master audio will be kept safely.";

    if (!confirm(confirmMsg)) return;

    setCleaning(true);
    try {
      const res = await api.clearStorage(purgeAll);
      alert(res.message);
      fetchStorage();
    } catch (err: any) {
      alert("Failed to clear storage: " + err.message);
    } finally {
      setCleaning(false);
    }
  };

  return (
    <>
      <Header
        title="Studio Settings & AI Engine Hub"
        subtitle="Configure OpenRouter LLM, Wan FLF2V Video Generation, High-CTR Thumbnail Engine, and local tool daemons"
      />

      <main className="p-8 space-y-6 flex-1 max-w-4xl mx-auto w-full">
        {/* 1. OpenRouter Universal API Key & Text Engine */}
        <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 space-y-6 shadow-xs relative overflow-hidden">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#E5E5EA] gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#EFF6FF] text-[#2563EB] flex items-center justify-center border border-[#BFDBFE]">
                <BrainCircuit className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-base font-bold text-[#1D1D1F]">
                    OpenRouter AI & Deep Research Engine
                  </h2>
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-[#EFF6FF] text-[#2563EB] border border-[#BFDBFE]">
                    592+ Models
                  </span>
                </div>
                <p className="text-xs text-[#86868B] mt-0.5">
                  Top SEO Research, Viral Rhymes & Catchy Kids Lyrics Writing, Character Bibles & Storyboard Engine
                </p>
              </div>
            </div>

            {/* Toggle Switch */}
            <div className="flex items-center gap-3 self-start sm:self-auto">
              <span className="text-xs font-semibold text-[#86868B]">
                {enabled ? (
                  <span className="text-[#059669] flex items-center gap-1 font-bold">
                    <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse"></span>
                    ON (Active)
                  </span>
                ) : (
                  <span className="text-[#6B7280]">OFF (Disabled)</span>
                )}
              </span>

              <button
                onClick={handleToggleOpenRouter}
                disabled={savingAI}
                className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                  enabled ? "bg-[#2563EB]" : "bg-[#D1D5DB]"
                }`}
                role="switch"
                aria-checked={enabled}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out ${
                    enabled ? "translate-x-5" : "translate-x-0"
                  }`}
                />
              </button>
            </div>
          </div>

          {/* Active Provider Banner */}
          <div className="bg-[#F8FAFC] border border-[#E2E8F0] p-3.5 rounded-xl flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <Bot className="w-4 h-4 text-[#3B82F6]" />
              <span className="text-[#64748B]">Active Text / SEO Engine:</span>
              <span className="font-bold text-[#0F172A]">
                {aiSettings?.active_provider || "Detecting..."}
              </span>
            </div>
            <span className="text-[11px] text-[#64748B]">
              {enabled && apiKey
                ? "⚡ High-IQ Deep Research & SEO Active"
                : "⚙️ Local Fallback Engine Active"}
            </span>
          </div>

          <div className="space-y-4">
            {/* API Key Input */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
                  <Key className="w-3.5 h-3.5 text-[#6B7280]" />
                  <span>OpenRouter API Key (Shared for LLM, Video & Image Generation)</span>
                  {apiKey && (
                    <span className="text-[11px] text-[#059669] font-semibold flex items-center gap-1">
                      <Check className="w-3 h-3 text-[#10B981]" />
                      (Saved in DB)
                    </span>
                  )}
                </label>
                <a
                  href="https://openrouter.ai/keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-[#2563EB] hover:underline flex items-center gap-1"
                >
                  <span>Get Free Key at openrouter.ai/keys</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>

              <div className="relative flex items-center">
                <input
                  type={showApiKey ? "text" : "password"}
                  placeholder="sk-or-v1-..."
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full bg-[#FAFAFA] border border-[#E5E5EA] rounded-xl px-3.5 py-2.5 text-xs font-mono text-[#1D1D1F] focus:bg-white focus:outline-none focus:border-[#2563EB] pr-20"
                />
                <div className="absolute right-2.5 flex items-center gap-1">
                  <button
                    type="button"
                    onClick={handleCopyKey}
                    className="p-1 text-[#86868B] hover:text-[#1D1D1F] cursor-pointer"
                    title="Copy Key"
                  >
                    {copiedKey ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="p-1 text-[#86868B] hover:text-[#1D1D1F] cursor-pointer"
                    title={showApiKey ? "Hide Key" : "Show Key"}
                  >
                    {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>

            {/* Model Selector & Quick Chips */}
            <div>
              <label className="text-xs font-bold text-[#1D1D1F] block mb-1.5 flex items-center gap-1.5">
                <Sliders className="w-3.5 h-3.5 text-[#6B7280]" />
                <span>Text / SEO Model (For Lyrics, Song Rhythm & 3D Storyboard)</span>
              </label>

              <select
                value={selectedModel}
                onChange={(e) => {
                  setSelectedModel(e.target.value);
                  setCustomModel("");
                }}
                className="w-full bg-[#FAFAFA] border border-[#E5E5EA] rounded-xl px-3 py-2.5 text-xs text-[#1D1D1F] font-medium focus:bg-white focus:outline-none focus:border-[#2563EB] cursor-pointer"
              >
                {aiSettings?.available_models.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name} {m.is_free ? "🎁 [FREE]" : "💎 [SOTA]"}
                  </option>
                ))}
              </select>

              {/* Quick Model Chips */}
              <div className="flex flex-wrap gap-1.5 mt-2.5">
                <span className="text-[10px] text-[#86868B] self-center mr-1 font-semibold">Recommended:</span>
                {[
                  { id: "openrouter/free", label: "🎁 OpenRouter Free Auto-Router (100% Free)" },
                  { id: "meta-llama/llama-3.3-70b-instruct:free", label: "🎁 Llama 3.3 70B (Free)" },
                  { id: "google/gemini-2.0-flash-exp:free", label: "🎁 Gemini 2.0 Flash (100% Free)" },
                  { id: "deepseek/deepseek-r1:free", label: "🎁 DeepSeek R1 (100% Free)" },
                  { id: "liquid/lfm-2.5-2.6b:free", label: "🎁 Liquid LFM (100% Free)" },
                  { id: "meta-llama/llama-3.3-70b-instruct", label: "Llama 3.3 70B (Paid SOTA)" },
                  { id: "qwen/qwen-2.5-72b-instruct", label: "Qwen 2.5 72B (Paid SOTA)" },
                  { id: "openai/gpt-4o", label: "GPT-4o (Paid Flagship)" },
                ].map((chip) => (
                  <button
                    key={chip.id}
                    type="button"
                    onClick={() => {
                      setSelectedModel(chip.id);
                      setCustomModel("");
                    }}
                    className={`text-[10px] px-2.5 py-1 rounded-lg border transition-all cursor-pointer ${
                      selectedModel === chip.id && !customModel
                        ? "bg-[#EFF6FF] border-[#BFDBFE] text-[#1D4ED8] font-bold"
                        : "bg-[#FAFAFA] border-[#E5E5EA] text-[#6B7280] hover:bg-white"
                    }`}
                  >
                    {chip.label}
                  </button>
                ))}
              </div>

              {/* Custom Model Input */}
              <div className="mt-3 pt-3 border-t border-[#E5E5EA]">
                <label className="text-[11px] font-semibold text-[#6B7280] block mb-1">
                  Or enter custom LLM ID from OpenRouter catalog:
                </label>
                <input
                  type="text"
                  placeholder="e.g. anthropic/claude-3.7-sonnet"
                  value={customModel}
                  onChange={(e) => setCustomModel(e.target.value)}
                  className="w-full bg-[#FAFAFA] border border-[#E5E5EA] rounded-xl px-3 py-1.5 text-xs font-mono text-[#1D1D1F] focus:bg-white focus:outline-none focus:border-[#2563EB]"
                />
              </div>
            </div>

            {/* Action Buttons: Save & Test Text Model */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
              <button
                type="button"
                onClick={handleTestConnection}
                disabled={testing}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-[#F1F5F9] text-[#475569] hover:bg-[#E2E8F0] border border-[#CBD5E1] transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
              >
                {testing ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-[#2563EB]" />
                ) : (
                  <Zap className="w-3.5 h-3.5 text-[#F59E0B]" />
                )}
                <span>{testing ? "Testing Connection..." : "Test OpenRouter Text Connection"}</span>
              </button>

              <button
                type="button"
                onClick={() => handleSaveAISettings()}
                disabled={savingAI}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-[#2563EB] text-white hover:bg-[#1D4ED8] shadow-xs transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
              >
                {saveSuccess ? (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    <span>Permanently Saved in DB!</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>{savingAI ? "Saving to DB..." : "Save All Settings"}</span>
                  </>
                )}
              </button>
            </div>

            {testResult && (
              <div className="bg-[#ECFDF5] border border-[#A7F3D0] p-3.5 rounded-xl text-xs space-y-1 animate-in fade-in duration-200">
                <div className="flex items-center gap-2 text-[#065F46] font-bold">
                  <CheckCircle2 className="w-4 h-4 text-[#10B981]" />
                  <span>Connection Verified! Response Time: {testResult.latency_ms} ms</span>
                </div>
                <p className="text-[11px] text-[#047857] pl-6 font-mono">
                  Model: {testResult.model} &bull; &ldquo;{testResult.response}&rdquo;
                </p>
              </div>
            )}

            {testError && (
              <div className="bg-[#FEF2F2] border border-[#FECACA] p-3.5 rounded-xl text-xs space-y-1 animate-in fade-in duration-200">
                <div className="flex items-center gap-2 text-[#991B1B] font-bold">
                  <XCircle className="w-4 h-4 text-[#EF4444]" />
                  <span>Connection Failed</span>
                </div>
                <p className="text-[11px] text-[#B91C1C] pl-6 font-mono">{testError}</p>
              </div>
            )}
          </div>
        </div>

        {/* 2. Wan Video Generation Engine (fal-ai/wan-flf2v) - Replaces Blender 3D */}
        <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 space-y-6 shadow-xs relative overflow-hidden">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#E5E5EA] gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#FAF5FF] text-[#9333EA] flex items-center justify-center border border-[#E9D5FF]">
                <Video className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-base font-bold text-[#1D1D1F]">
                    Wan Video Generation Engine
                  </h2>
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-[#FAF5FF] text-[#9333EA] border border-[#E9D5FF]">
                    {videoProvider === "wan" || useWanVideo ? "Wan 2.1 FLF2V (Active)" : "Local Storybook 3D (Active)"}
                  </span>
                </div>
                <p className="text-xs text-[#86868B] mt-0.5">
                  First-Frame to Last-Frame (FLF2V) AI 3D Animation & Scene Continuity Engine
                </p>
              </div>
            </div>

            {/* Video Toggle Switch: ON (Wan FLF2V) / OFF (Local Storybook 3D) */}
            <div className="flex items-center gap-3 self-start sm:self-auto">
              <span className="text-xs font-semibold text-[#86868B]">
                {videoProvider === "wan" || useWanVideo ? (
                  <span className="text-[#059669] flex items-center gap-1 font-bold">
                    <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse"></span>
                    ON (Wan FLF2V Active)
                  </span>
                ) : (
                  <span className="text-[#6B7280]">OFF (Local 3D Storybook Engine)</span>
                )}
              </span>

              <button
                onClick={async () => {
                  const nextWan = !(videoProvider === "wan" || useWanVideo);
                  const nextProvider = nextWan ? "wan" : "local";
                  setVideoProvider(nextProvider);
                  setUseWanVideo(nextWan);
                  await handleSaveAISettings(enabled, thumbEnabled, autoSongEnabled, nextProvider, nextWan);
                }}
                disabled={savingAI}
                className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                  videoProvider === "wan" || useWanVideo ? "bg-[#9333EA]" : "bg-[#D1D5DB]"
                }`}
                role="switch"
                aria-checked={videoProvider === "wan" || useWanVideo}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out ${
                    videoProvider === "wan" || useWanVideo ? "translate-x-5" : "translate-x-0"
                  }`}
                />
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {/* OPTIONAL AI PROVIDER TOGGLES GRID (Section 2 of Safe Integration Spec) */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 bg-[#FAF5FF] border border-[#E9D5FF] rounded-2xl">
              {/* 1. Use Wan Video Generation */}
              <div className="bg-white p-3 rounded-xl border border-[#E9D5FF] flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold text-[#1D1D1F] block">Use Wan Video</span>
                  <span className="text-[10px] text-[#6E6E73]">{useWanVideo ? "ON (Fal.ai FLF2V)" : "OFF (Local 3D)"}</span>
                </div>
                <input
                  type="checkbox"
                  checked={useWanVideo}
                  onChange={async (e) => {
                    const checked = e.target.checked;
                    setUseWanVideo(checked);
                    setVideoProvider(checked ? "wan" : "local");
                    await handleSaveAISettings(enabled, thumbEnabled, autoSongEnabled, checked ? "wan" : "local", checked);
                  }}
                  className="w-4 h-4 text-[#9333EA] rounded border-[#E5E5EA] focus:ring-[#9333EA] cursor-pointer"
                />
              </div>

              {/* 2. Use AI Thumbnail Generation */}
              <div className="bg-white p-3 rounded-xl border border-[#E9D5FF] flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold text-[#1D1D1F] block">Use AI Thumbnail</span>
                  <span className="text-[10px] text-[#6E6E73]">{useAiThumbnail ? "ON (AI Image + Overlay)" : "OFF (Graphic Engine)"}</span>
                </div>
                <input
                  type="checkbox"
                  checked={useAiThumbnail}
                  onChange={async (e) => {
                    const checked = e.target.checked;
                    setUseAiThumbnail(checked);
                    await handleSaveAISettings(enabled, thumbEnabled, autoSongEnabled, videoProvider, useWanVideo, checked);
                  }}
                  className="w-4 h-4 text-[#9333EA] rounded border-[#E5E5EA] focus:ring-[#9333EA] cursor-pointer"
                />
              </div>

              {/* 3. Use AI Reference Image */}
              <div className="bg-white p-3 rounded-xl border border-[#E9D5FF] flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold text-[#1D1D1F] block">Use AI Reference Images</span>
                  <span className="text-[10px] text-[#6E6E73]">{useAiReferenceImages ? "ON (AI Continuity)" : "OFF (Procedural)"}</span>
                </div>
                <input
                  type="checkbox"
                  checked={useAiReferenceImages}
                  onChange={async (e) => {
                    const checked = e.target.checked;
                    setUseAiReferenceImages(checked);
                    await handleSaveAISettings(enabled, thumbEnabled, autoSongEnabled, videoProvider, useWanVideo, useAiThumbnail, checked);
                  }}
                  className="w-4 h-4 text-[#9333EA] rounded border-[#E5E5EA] focus:ring-[#9333EA] cursor-pointer"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* FAL API Key Input & Update */}
              <div>
                <label className="text-xs font-bold text-[#1D1D1F] block mb-1.5 flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <Key className="w-3.5 h-3.5 text-[#6B7280]" />
                    <span>Fal.ai API Key (FAL_KEY)</span>
                  </div>
                  {aiSettings?.fal_key_configured ? (
                    <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                      ✓ Key Configured
                    </span>
                  ) : (
                    <span className="text-[10px] font-bold text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
                      ⚠ Key Needed for Live Wan
                    </span>
                  )}
                </label>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <input
                      type={showFalKey ? "text" : "password"}
                      value={falKey}
                      onChange={(e) => setFalKey(e.target.value)}
                      placeholder="Enter fal_key_..."
                      className="w-full bg-[#FAFAFA] border border-[#E5E5EA] rounded-xl pl-3 pr-14 py-2.5 text-xs text-[#1D1D1F] font-mono focus:bg-white focus:outline-none focus:border-[#9333EA]"
                    />
                    <button
                      type="button"
                      onClick={() => setShowFalKey(!showFalKey)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[#86868B] hover:text-[#1D1D1F] text-xs font-medium cursor-pointer"
                    >
                      {showFalKey ? "Hide" : "Show"}
                    </button>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleSaveAISettings()}
                    disabled={savingAI || !falKey.trim()}
                    className="px-3.5 py-2.5 bg-[#9333EA] text-white rounded-xl text-xs font-bold hover:bg-[#7E22CE] transition-all cursor-pointer disabled:opacity-50 flex items-center gap-1.5 shadow-xs shrink-0"
                  >
                    <span>{falKeySaved ? "✓ Updated" : savingAI ? "Saving..." : "Update Key"}</span>
                  </button>
                </div>
                <p className="text-[11px] text-[#86868B] mt-1">
                  Used securely server-side for <code className="bg-slate-100 px-1 py-0.5 rounded">fal-ai/wan-flf2v</code>. Never exposed to browser or client.
                </p>
              </div>

              {/* Wan Model Selection */}
              <div>
                <label className="text-xs font-bold text-[#1D1D1F] block mb-1.5 flex items-center gap-1.5">
                  <Film className="w-3.5 h-3.5 text-[#6B7280]" />
                  <span>Wan Model Endpoint</span>
                </label>
                <select
                  value={wanModel}
                  onChange={(e) => setWanModel(e.target.value)}
                  className="w-full bg-[#FAFAFA] border border-[#E5E5EA] rounded-xl px-3 py-2.5 text-xs text-[#1D1D1F] font-medium focus:bg-white focus:outline-none focus:border-[#9333EA] cursor-pointer"
                >
                  <option value="fal-ai/wan-flf2v">fal-ai/wan-flf2v (First-Frame to Last-Frame - Recommended)</option>
                  <option value="fal-ai/wan/v2.1/image-to-video">fal-ai/wan/v2.1/image-to-video (Image to Video)</option>
                  <option value="fal-ai/wan/v2.1/text-to-video">fal-ai/wan/v2.1/text-to-video (Text to Video)</option>
                </select>

                <div className="mt-3">
                  <label className="text-xs font-bold text-[#1D1D1F] block mb-1.5 flex items-center gap-1.5">
                    <Monitor className="w-3.5 h-3.5 text-[#6B7280]" />
                    <span>Resolution</span>
                  </label>
                  <select
                    value={wanResolution}
                    onChange={(e) => setWanResolution(e.target.value)}
                    className="w-full bg-[#FAFAFA] border border-[#E5E5EA] rounded-xl px-3 py-2 text-xs text-[#1D1D1F] font-medium focus:bg-white focus:outline-none focus:border-[#9333EA] cursor-pointer"
                  >
                    <option value="720p">720p (Default - Fast & High Quality)</option>
                    <option value="1080p">1080p (Full HD)</option>
                    <option value="480p">480p (Fast Draft)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Video Aspect Ratio Selector */}
            <div>
              <label className="text-xs font-bold text-[#1D1D1F] block mb-1.5 flex items-center gap-1.5">
                <Clapperboard className="w-3.5 h-3.5 text-[#6B7280]" />
                <span>Video Aspect Ratio</span>
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setVideoAspectRatio("16:9")}
                  className={`px-3 py-2 rounded-xl text-xs font-bold border transition-all flex items-center justify-center gap-2 cursor-pointer ${
                    videoAspectRatio === "16:9"
                      ? "bg-[#FAF5FF] border-[#9333EA] text-[#9333EA] shadow-xs"
                      : "bg-[#FAFAFA] border-[#E5E5EA] text-[#6B7280] hover:bg-white"
                  }`}
                >
                  <Monitor className="w-4 h-4" />
                  <span>16:9 (YouTube Widescreen - Default)</span>
                </button>

                <button
                  type="button"
                  onClick={() => setVideoAspectRatio("9:16")}
                  className={`px-3 py-2 rounded-xl text-xs font-bold border transition-all flex items-center justify-center gap-2 cursor-pointer ${
                    videoAspectRatio === "9:16"
                      ? "bg-[#FAF5FF] border-[#9333EA] text-[#9333EA] shadow-xs"
                      : "bg-[#FAFAFA] border-[#E5E5EA] text-[#6B7280] hover:bg-white"
                  }`}
                >
                  <Smartphone className="w-4 h-4" />
                  <span>9:16 (Shorts / Reels / TikTok)</span>
                </button>
              </div>
            </div>

            {/* Fast Development Test Mode Toggle */}
            <div className="flex items-center justify-between p-3.5 rounded-xl bg-[#FAF5FF] border border-[#E9D5FF]">
              <div className="flex items-center gap-2.5">
                <Sparkles className="w-4 h-4 text-[#9333EA] shrink-0" />
                <div>
                  <span className="text-xs font-bold text-[#1D1D1F] block">
                    Fast Development Test Mode (AI_PROVIDER_TEST_MODE)
                  </span>
                  <span className="text-[11px] text-[#6E6E73]">
                    When enabled, generates ONLY 1 thumbnail, 1 reference image, and 1 video scene to verify Wan FLF2V and character continuity safely.
                  </span>
                </div>
              </div>
              <input
                type="checkbox"
                checked={aiProviderTestMode || wanTestMode}
                onChange={async (e) => {
                  const checked = e.target.checked;
                  setAiProviderTestMode(checked);
                  setWanTestMode(checked);
                  await handleSaveAISettings(enabled, thumbEnabled, autoSongEnabled, videoProvider, useWanVideo, useAiThumbnail, useAiReferenceImages, checked);
                }}
                className="w-4 h-4 text-[#9333EA] rounded border-[#E5E5EA] focus:ring-[#9333EA] cursor-pointer"
              />
            </div>

            {/* Save Button for Video Provider Settings */}
            <div className="flex items-center justify-between pt-2 border-t border-[#E5E5EA]">
              <div className="text-[11px] text-[#6E6E73]">
                {videoProvider === "wan" || useWanVideo
                  ? "Wan FLF2V AI video generation active."
                  : "Local 3D Storybook engine is active (Blender-free)."}
              </div>

              <button
                type="button"
                onClick={() => handleSaveAISettings()}
                disabled={savingAI}
                className="px-5 py-2.5 bg-[#9333EA] text-white rounded-xl text-xs font-bold hover:bg-[#7E22CE] transition-all cursor-pointer disabled:opacity-50 flex items-center gap-1.5 shadow-xs"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>{savingAI ? "Saving..." : "Save Wan & Provider Settings"}</span>
              </button>
            </div>
          </div>
        </div>

        {/* 3. High-CTR & High-CPM YouTube Kids Thumbnail Engine */}
        <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 space-y-6 shadow-xs relative overflow-hidden">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#E5E5EA] gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#FFFBEB] text-[#D97706] flex items-center justify-center border border-[#FDE68A]">
                <ImageIcon className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-base font-bold text-[#1D1D1F]">
                    High-CTR YouTube Kids Thumbnail Engine
                  </h2>
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-[#FFFBEB] text-[#D97706] border border-[#FDE68A]">
                    High CPM Cues
                  </span>
                </div>
                <p className="text-xs text-[#86868B] mt-0.5">
                  Generates vibrant 3D Pixar YouTube covers with 3D title text, action hooks, and high-CTR badges
                </p>
              </div>
            </div>

            {/* Thumbnail Toggle Switch */}
            <div className="flex items-center gap-3 self-start sm:self-auto">
              <span className="text-xs font-semibold text-[#86868B]">
                {thumbEnabled ? (
                  <span className="text-[#059669] flex items-center gap-1 font-bold">
                    <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse"></span>
                    ON (Active)
                  </span>
                ) : (
                  <span className="text-[#6B7280]">OFF</span>
                )}
              </span>

              <button
                onClick={handleToggleThumbnail}
                disabled={savingAI}
                className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                  thumbEnabled ? "bg-[#D97706]" : "bg-[#D1D5DB]"
                }`}
                role="switch"
                aria-checked={thumbEnabled}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out ${
                    thumbEnabled ? "translate-x-5" : "translate-x-0"
                  }`}
                />
              </button>
            </div>
          </div>

          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Thumbnail Model Selector */}
              <div>
                <label className="text-xs font-bold text-[#1D1D1F] block mb-1.5 flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-[#6B7280]" />
                  <span>Thumbnail Generator Model</span>
                </label>
                <select
                  value={thumbModel}
                  onChange={(e) => setThumbModel(e.target.value)}
                  className="w-full bg-[#FAFAFA] border border-[#E5E5EA] rounded-xl px-3 py-2.5 text-xs text-[#1D1D1F] font-medium focus:bg-white focus:outline-none focus:border-[#D97706] cursor-pointer"
                >
                  {(aiSettings?.available_thumbnail_models || [
                    { id: "high_ctr_graphic", name: "High-CTR 3D Visual Graphic Engine (Local Fast & Free)" },
                    { id: "openai/dall-e-3", name: "DALL-E 3 (OpenAI High-CTR Pixar Cover)" },
                    { id: "black-forest-labs/flux-1-schnell", name: "Flux 1 Schnell (Ultra Fast)" },
                    { id: "black-forest-labs/flux-1-dev", name: "Flux 1 Dev (High Fidelity)" },
                    { id: "google/imagen-3", name: "Google Imagen 3" },
                  ]).map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Thumbnail Aspect Ratio Selector */}
              <div>
                <label className="text-xs font-bold text-[#1D1D1F] block mb-1.5 flex items-center gap-1.5">
                  <Clapperboard className="w-3.5 h-3.5 text-[#6B7280]" />
                  <span>Thumbnail Aspect Ratio</span>
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setThumbAspectRatio("16:9")}
                    className={`px-3 py-2 rounded-xl text-xs font-bold border transition-all flex items-center justify-center gap-2 cursor-pointer ${
                      thumbAspectRatio === "16:9"
                        ? "bg-[#FFFBEB] border-[#D97706] text-[#D97706] shadow-xs"
                        : "bg-[#FAFAFA] border-[#E5E5EA] text-[#6B7280] hover:bg-white"
                    }`}
                  >
                    <Monitor className="w-4 h-4" />
                    <span>16:9 (1280x720 - YouTube)</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setThumbAspectRatio("9:16")}
                    className={`px-3 py-2 rounded-xl text-xs font-bold border transition-all flex items-center justify-center gap-2 cursor-pointer ${
                      thumbAspectRatio === "9:16"
                        ? "bg-[#FFFBEB] border-[#D97706] text-[#D97706] shadow-xs"
                        : "bg-[#FAFAFA] border-[#E5E5EA] text-[#6B7280] hover:bg-white"
                    }`}
                  >
                    <Smartphone className="w-4 h-4" />
                    <span>9:16 (1080x1920 - Shorts)</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Test Thumbnail Button */}
            <div className="flex items-center justify-between pt-2">
              <button
                type="button"
                onClick={handleTestThumbnail}
                disabled={testingThumb}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-[#FFFBEB] text-[#D97706] hover:bg-[#FEF3C7] border border-[#FDE68A] transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
              >
                {testingThumb ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-[#D97706]" />
                ) : (
                  <ImageIcon className="w-3.5 h-3.5 text-[#D97706]" />
                )}
                <span>{testingThumb ? "Generating Sample..." : "Test High-CTR Thumbnail Generator"}</span>
              </button>

              <button
                type="button"
                onClick={() => handleSaveAISettings()}
                disabled={savingAI}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-[#D97706] text-white hover:bg-[#B45309] shadow-xs transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Save Thumbnail Config</span>
              </button>
            </div>

            {thumbTestResult && (
              <div className="bg-[#ECFDF5] border border-[#A7F3D0] p-3.5 rounded-xl text-xs space-y-1 animate-in fade-in duration-200">
                <div className="flex items-center gap-2 text-[#065F46] font-bold">
                  <CheckCircle2 className="w-4 h-4 text-[#10B981]" />
                  <span>{thumbTestResult.message}</span>
                </div>
                <p className="text-[11px] text-[#047857] pl-6 font-mono">
                  Model: {thumbTestResult.model} &bull; Format: {thumbTestResult.aspect_ratio} &bull; Output Size: {thumbTestResult.file_size} bytes
                </p>
              </div>
            )}

            {thumbTestError && (
              <div className="bg-[#FEF2F2] border border-[#FECACA] p-3.5 rounded-xl text-xs space-y-1 animate-in fade-in duration-200">
                <div className="flex items-center gap-2 text-[#991B1B] font-bold">
                  <XCircle className="w-4 h-4 text-[#EF4444]" />
                  <span>Thumbnail Test Error</span>
                </div>
                <p className="text-[11px] text-[#B91C1C] pl-6 font-mono">{thumbTestError}</p>
              </div>
            )}
          </div>
        </div>

        {/* 4. Music & Song Production Mode (Auto Neural Synthesizer vs Manual Suno AI) */}
        <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 space-y-6 shadow-xs relative overflow-hidden">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#E5E5EA] gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#FFF7ED] text-[#EA580C] flex items-center justify-center border border-[#FED7AA]">
                <Music className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-base font-bold text-[#1D1D1F]">
                    Music & Song Production Engine
                  </h2>
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-[#FFF7ED] text-[#EA580C] border border-[#FED7AA]">
                    {autoSongEnabled ? "Auto Synthesizer" : "Manual Suno AI Mode"}
                  </span>
                </div>
                <p className="text-xs text-[#86868B] mt-0.5">
                  Choose between automated local neural music synthesis or manual Suno AI generation with drag-and-drop audio upload
                </p>
              </div>
            </div>

            {/* Auto Song Toggle */}
            <div className="flex items-center gap-3 self-start sm:self-auto">
              <span className="text-xs font-semibold text-[#86868B]">
                {autoSongEnabled ? (
                  <span className="text-[#059669] flex items-center gap-1 font-bold">
                    <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse"></span>
                    AUTO SYNTHESIZER (ON)
                  </span>
                ) : (
                  <span className="text-[#EA580C] font-bold flex items-center gap-1">
                    <Radio className="w-3.5 h-3.5" />
                    MANUAL SUNO AI MODE (OFF)
                  </span>
                )}
              </span>

              <button
                onClick={handleToggleAutoSong}
                disabled={savingAI}
                className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                  autoSongEnabled ? "bg-[#EA580C]" : "bg-[#D1D5DB]"
                }`}
                role="switch"
                aria-checked={autoSongEnabled}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out ${
                    autoSongEnabled ? "translate-x-5" : "translate-x-0"
                  }`}
                />
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className={`p-4 rounded-xl border transition-all ${autoSongEnabled ? "bg-[#FFF7ED] border-[#FED7AA]" : "bg-[#FAFAFA] border-[#E5E5EA] opacity-60"}`}>
              <div className="flex items-center gap-2 font-bold text-xs text-[#9A3412] mb-1">
                <Sparkles className="w-4 h-4 text-[#EA580C]" />
                <span>Auto Synthesizer Mode (When ON)</span>
              </div>
              <p className="text-[11px] text-[#7C2D12] leading-relaxed">
                Automatically composes melodies and vocal tracks locally without manual intervention. Great for 100% automated batch pipelines.
              </p>
            </div>

            <div className={`p-4 rounded-xl border transition-all ${!autoSongEnabled ? "bg-[#FFF7ED] border-[#FED7AA]" : "bg-[#FAFAFA] border-[#E5E5EA] opacity-60"}`}>
              <div className="flex items-center gap-2 font-bold text-xs text-[#9A3412] mb-1">
                <Radio className="w-4 h-4 text-[#EA580C]" />
                <span>Manual Suno AI Mode (When OFF)</span>
              </div>
              <p className="text-[11px] text-[#7C2D12] leading-relaxed">
                Generates high-engagement Suno AI prompts, catchy kids titles, and tagged lyrics. Paste into Suno.ai, download the song, and upload it here to auto-sync scenes and subtitles (.srt).
              </p>
            </div>
          </div>
        </div>

        {/* 4. Local Tool Servers & Resource Optimizer */}
        <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 space-y-5 shadow-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#E5E5EA] gap-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#F0FDF4] text-[#16A34A] flex items-center justify-center border border-[#BBF7D0]">
                <Activity className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-[#1D1D1F]">
                  Local Tool Servers & Resource Optimizer
                </h2>
                <p className="text-xs text-[#86868B]">
                  Start or Stop individual local daemons to free up RAM & CPU when not in use
                </p>
              </div>
            </div>

            <button
              onClick={handleStopUnused}
              disabled={serviceActionLoading === "optimize"}
              className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-[#FEF2F2] text-[#DC2626] hover:bg-[#FEE2E2] border border-[#FECACA] transition-all flex items-center gap-1.5 cursor-pointer self-start sm:self-auto disabled:opacity-50"
            >
              <PowerOff className="w-3.5 h-3.5" />
              <span>
                {serviceActionLoading === "optimize" ? "Optimizing..." : "⚡ Stop Unused Servers"}
              </span>
            </button>
          </div>

          {optimizeMessage && (
            <div className="p-3 bg-[#ECFDF5] border border-[#A7F3D0] rounded-xl text-xs text-[#065F46] font-medium animate-in fade-in">
              {optimizeMessage}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            {services.map((svc) => (
              <div
                key={svc.key}
                className="p-4 bg-[#FAFAFA] rounded-xl border border-[#E5E5EA] flex items-center justify-between gap-3"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={`w-2.5 h-2.5 rounded-full ${
                        svc.running ? "bg-[#10B981] animate-pulse" : "bg-[#9CA3AF]"
                      }`}
                    />
                    <span className="text-xs font-bold text-[#1D1D1F]">{svc.name}</span>
                    <span className="text-[10px] text-[#6B7280] font-mono">
                      (Port: {svc.port || "N/A"})
                    </span>
                  </div>
                  <p className="text-[11px] text-[#86868B]">{svc.description}</p>
                  {svc.pid && (
                    <span className="text-[10px] font-mono text-[#059669] block">
                      PID: {svc.pid}
                    </span>
                  )}
                </div>

                {svc.can_toggle ? (
                  <button
                    onClick={() => handleToggleService(svc.key, svc.running)}
                    disabled={serviceActionLoading === svc.key}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1 disabled:opacity-50 ${
                      svc.running
                        ? "bg-[#FEF2F2] text-[#DC2626] hover:bg-[#FEE2E2] border border-[#FECACA]"
                        : "bg-[#F0FDF4] text-[#16A34A] hover:bg-[#DCFCE7] border border-[#BBF7D0]"
                    }`}
                  >
                    <Power className="w-3 h-3" />
                    <span>
                      {serviceActionLoading === svc.key
                        ? "Working..."
                        : svc.running
                        ? "Turn OFF"
                        : "Turn ON"}
                    </span>
                  </button>
                ) : (
                  <span className="text-[10px] font-bold px-2 py-1 rounded-lg bg-[#EFF6FF] text-[#2563EB] border border-[#BFDBFE]">
                    ALWAYS ON
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* 5. Storage & Disk Cache Management */}
        <div className="bg-white border border-[#E5E5EA] rounded-2xl p-6 space-y-5 shadow-xs">
          <div className="flex items-center justify-between pb-4 border-b border-[#E5E5EA]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#FFF7ED] text-[#FF6B00] flex items-center justify-center border border-[#FED7AA]">
                <HardDrive className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-[#1D1D1F]">Storage & Disk Cache Management</h2>
                <p className="text-xs text-[#86868B]">
                  Inspect and purge temporary frame caches, intermediate scratch files, and logs
                </p>
              </div>
            </div>

            <button
              onClick={fetchStorage}
              className="text-xs text-[#FF6B00] hover:text-[#EA580C] font-semibold flex items-center gap-1.5 bg-[#FFF7ED] px-3 py-1.5 rounded-xl transition-all cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Refresh Disk Stats</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-[#FAFAFA] p-4 rounded-xl border border-[#E5E5EA]">
              <span className="text-[11px] font-semibold text-[#86868B] uppercase tracking-wider block">
                Total Space Used
              </span>
              <span className="text-2xl font-bold text-[#1D1D1F] mt-1 block">
                {storage?.total_formatted || "Calculating..."}
              </span>
              <span className="text-[10px] text-[#86868B] mt-1 block">
                {storage?.project_count || 0} active projects
              </span>
            </div>

            <div className="bg-[#FAFAFA] p-4 rounded-xl border border-[#E5E5EA]">
              <span className="text-[11px] font-semibold text-[#86868B] uppercase tracking-wider block">
                Project Videos & Audio
              </span>
              <span className="text-2xl font-bold text-[#1D1D1F] mt-1 block">
                {storage?.projects_formatted || "0 B"}
              </span>
              <span className="text-[10px] text-[#86868B] mt-1 block truncate">
                {storage?.project_dir || "./projects"}
              </span>
            </div>

            <div className="bg-[#FAFAFA] p-4 rounded-xl border border-[#E5E5EA]">
              <span className="text-[11px] font-semibold text-[#86868B] uppercase tracking-wider block">
                Engine Logs Cache
              </span>
              <span className="text-2xl font-bold text-[#1D1D1F] mt-1 block">
                {storage?.logs_formatted || "0 B"}
              </span>
              <span className="text-[10px] text-[#86868B] mt-1 block">
                App, LLM & FFmpeg diagnostic trails
              </span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 bg-[#FFFBEB] border border-[#FDE68A] p-4 rounded-xl">
            <div className="flex items-start gap-2.5">
              <AlertTriangle className="w-4 h-4 text-[#D97706] shrink-0 mt-0.5" />
              <div>
                <span className="text-xs font-bold text-[#92400E] block">Disk Optimization</span>
                <span className="text-[11px] text-[#B45309] block mt-0.5">
                  Rendering 3D scenes accumulates intermediate video and audio buffers. Clean safely without losing final exports.
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <button
                disabled={cleaning}
                onClick={() => handleClearCache(false)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#FEF3C7] text-[#92400E] hover:bg-[#FDE68A] border border-[#FCD34D] transition-all cursor-pointer disabled:opacity-50"
              >
                {cleaning ? "Cleaning..." : "Clear Temp Cache"}
              </button>
              <button
                disabled={cleaning}
                onClick={() => handleClearCache(true)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#DC2626] text-white hover:bg-[#B91C1C] transition-all cursor-pointer disabled:opacity-50 flex items-center gap-1"
              >
                <Trash2 className="w-3 h-3" />
                <span>Reset All Projects</span>
              </button>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
