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
  const [selectedModel, setSelectedModel] = useState("deepseek/deepseek-r1:free");
  const [customModel, setCustomModel] = useState("");
  const [savingAI, setSavingAI] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [copiedKey, setCopiedKey] = useState(false);

  // Testing State
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
      setSelectedModel(data.openrouter_model || "deepseek/deepseek-r1:free");
      if (data.openrouter_api_key) {
        setApiKey(data.openrouter_api_key);
      }
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

  const handleSaveAISettings = async (overrideEnabled?: boolean) => {
    setSavingAI(true);
    setSaveSuccess(false);
    setTestResult(null);
    setTestError(null);

    const isEnabled = overrideEnabled !== undefined ? overrideEnabled : enabled;
    const modelToSave = customModel.trim() ? customModel.trim() : selectedModel;

    try {
      const updated = await api.updateAISettings({
        openrouter_enabled: isEnabled,
        openrouter_api_key: apiKey.trim() ? apiKey.trim() : undefined,
        openrouter_model: modelToSave,
      });
      setAiSettings(updated);
      setEnabled(updated.openrouter_enabled);
      if (updated.openrouter_api_key) {
        setApiKey(updated.openrouter_api_key);
      }
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      alert("Failed to save AI settings: " + err.message);
    } finally {
      setSavingAI(false);
    }
  };

  const handleToggleOpenRouter = async () => {
    const nextState = !enabled;
    setEnabled(nextState);
    await handleSaveAISettings(nextState);
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
        title="Studio Settings & Tool Lifecycle Manager"
        subtitle="Manage OpenRouter LLM, on-demand local tool servers, and disk storage optimization"
      />

      <main className="p-8 space-y-6 flex-1 max-w-4xl mx-auto w-full">
        {/* OpenRouter AI & Deep Research Engine Card */}
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
                  Top SEO Research, Viral Rhymes & Cocomelon Lyrics Writing, Character Bibles & Storyboard Engine
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
              <span className="text-[#64748B]">Active AI Engine:</span>
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
            {/* API Key Input (Permanently Saved in SQLite DB + .env) */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-bold text-[#1D1D1F] flex items-center gap-1.5">
                  <Key className="w-3.5 h-3.5 text-[#6B7280]" />
                  <span>OpenRouter API Key (Permanent Database Storage)</span>
                  {apiKey && (
                    <span className="text-[11px] text-[#059669] font-semibold flex items-center gap-1">
                      <Check className="w-3 h-3 text-[#10B981]" />
                      (Permanently Saved)
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

            {/* Model Selector & Quick SEO/Song Chips */}
            <div>
              <label className="text-xs font-bold text-[#1D1D1F] block mb-1.5 flex items-center gap-1.5">
                <Sliders className="w-3.5 h-3.5 text-[#6B7280]" />
                <span>Selected Model (For SEO, Lyrics, Song Rhythm & 3D Storyboard)</span>
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
                    {m.name} {m.is_free ? "🎁 [100% FREE]" : "💎 [SOTA]"}
                  </option>
                ))}
              </select>

              {/* Quick Model Chips */}
              <div className="flex flex-wrap gap-1.5 mt-2.5">
                <span className="text-[10px] text-[#86868B] self-center mr-1 font-semibold">Recommended:</span>
                {[
                  { id: "deepseek/deepseek-r1:free", label: "DeepSeek R1 (Free - SEO & Rhymes)" },
                  { id: "google/gemini-2.0-flash-exp:free", label: "Gemini 2.0 Flash (Free - Fast SEO)" },
                  { id: "meta-llama/llama-3.3-70b-instruct:free", label: "Llama 3.3 70B (Free SOTA)" },
                  { id: "openrouter/free", label: "Auto Free Router" },
                  { id: "anthropic/claude-3.5-sonnet", label: "Claude 3.5 Sonnet (Best Songwriter)" },
                  { id: "deepseek/deepseek-chat", label: "DeepSeek V3 (Fast)" },
                  { id: "openai/gpt-4o", label: "GPT-4o (OpenAI)" },
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

              {/* Custom Model Input for any of 592 models */}
              <div className="mt-3 pt-3 border-t border-[#E5E5EA]">
                <label className="text-[11px] font-semibold text-[#6B7280] block mb-1">
                  Or enter any custom model ID from OpenRouter&apos;s 592+ catalog:
                </label>
                <input
                  type="text"
                  placeholder="e.g. anthropic/claude-3.7-sonnet, qwen/qwen-2.5-72b-instruct"
                  value={customModel}
                  onChange={(e) => setCustomModel(e.target.value)}
                  className="w-full bg-[#FAFAFA] border border-[#E5E5EA] rounded-xl px-3 py-1.5 text-xs font-mono text-[#1D1D1F] focus:bg-white focus:outline-none focus:border-[#2563EB]"
                />
              </div>
            </div>

            {/* Action Buttons: Save & Test */}
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
                <span>{testing ? "Testing Connection..." : "Test OpenRouter Connection"}</span>
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
                    <span>{savingAI ? "Saving to DB..." : "Save Key & Settings"}</span>
                  </>
                )}
              </button>
            </div>

            {/* Test Results Card */}
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

        {/* Interactive Tool Servers & Resource Optimizer Card */}
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

        {/* Storage Management & Cache Cleaner Card */}
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
