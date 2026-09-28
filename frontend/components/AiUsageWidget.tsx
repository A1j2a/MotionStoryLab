"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface UsageStat {
  provider: string;
  model: string;
  call_count: number;
  last_used: string;
}

export default function AiUsageWidget() {
  const [stats, setStats] = useState<UsageStat[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const data = await api.getAiUsageStats();
      setStats(data);
    } catch {
      // backend offline
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const total = stats.reduce((s, r) => s + r.call_count, 0);

  const providerColor: Record<string, string> = {
    OpenRouter: "#6366f1",
    Ollama: "#10b981",
    Claude: "#f59e0b",
    OmniRoute: "#3b82f6",
  };

  return (
    <div style={{ padding: "16px 0 0" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, color: "#1e293b" }}>AI Usage Stats</div>
          <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 2 }}>
            {loading ? "Loading..." : `${total} total calls across all providers`}
          </div>
        </div>
        <button
          onClick={load}
          style={{
            fontSize: 11,
            color: "#64748b",
            background: "#f1f5f9",
            border: "1px solid #e2e8f0",
            borderRadius: 6,
            padding: "4px 10px",
            cursor: "pointer",
          }}
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <div style={{ height: 60, display: "flex", alignItems: "center", justifyContent: "center", color: "#94a3b8", fontSize: 12 }}>
          Loading usage data...
        </div>
      ) : stats.length === 0 ? (
        <div style={{ height: 60, display: "flex", alignItems: "center", justifyContent: "center", color: "#94a3b8", fontSize: 12, background: "#f8fafc", borderRadius: 8, border: "1px dashed #e2e8f0" }}>
          No AI calls recorded yet. Usage will appear after first AI generation.
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {stats.map((s, i) => {
            const pct = total > 0 ? Math.round((s.call_count / total) * 100) : 0;
            const color = providerColor[s.provider] || "#8b5cf6";
            const shortModel = s.model.length > 36 ? s.model.slice(0, 36) + "..." : s.model;
            const lastUsed = s.last_used
              ? new Date(s.last_used).toLocaleDateString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })
              : "-";

            return (
              <div key={i} style={{ background: "#f8fafc", borderRadius: 8, padding: "10px 12px", border: "1px solid #e9edf2" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{
                      fontSize: 10,
                      fontWeight: 600,
                      color: "#fff",
                      background: color,
                      borderRadius: 4,
                      padding: "2px 6px",
                      letterSpacing: "0.3px",
                    }}>
                      {s.provider}
                    </span>
                    <span style={{ fontSize: 11, color: "#475569", fontFamily: "monospace" }}>{shortModel}</span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ fontSize: 12, fontWeight: 700, color: "#1e293b" }}>{s.call_count}</span>
                    <span style={{ fontSize: 11, color: "#94a3b8" }}>{pct}%</span>
                  </div>
                </div>
                <div style={{ background: "#e9edf2", borderRadius: 3, height: 4, overflow: "hidden" }}>
                  <div style={{
                    height: "100%",
                    width: `${pct}%`,
                    background: color,
                    borderRadius: 3,
                    transition: "width 0.4s ease",
                  }} />
                </div>
                <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 4, textAlign: "right" }}>
                  Last: {lastUsed}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
