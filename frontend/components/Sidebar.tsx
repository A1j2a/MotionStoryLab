"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Film,
  PlusCircle,
  Clapperboard,
  Users2,
  FolderArchive,
  Music,
  Cpu,
  CheckCircle,
  Settings,
  Terminal,
  Sparkles,
  Layers,
  UploadCloud,
} from "lucide-react";
import { HealthStatus } from "./HealthStatus";

const NAV_ITEMS = [
  { href: "/", label: "Studio Dashboard (10-Step)", icon: LayoutDashboard, highlight: true },
  { href: "/studio", label: "🎬 Manual Workflow Studio", icon: UploadCloud, highlight: false },
  { href: "/projects", label: "Projects", icon: Film },
  { href: "/workflow", label: "Engine Workflow", icon: Layers },
  { href: "/scenes", label: "Scene Editor", icon: Clapperboard },
  { href: "/characters", label: "Character Bible", icon: Users2 },
  { href: "/assets", label: "Asset Library", icon: FolderArchive },
  { href: "/audio", label: "Audio Studio", icon: Music },
  { href: "/render", label: "Render Pipeline", icon: Cpu },
  { href: "/approval", label: "Video Approval & SEO", icon: CheckCircle },
  { href: "/settings", label: "Settings", icon: Settings },
  { href: "/logs", label: "Live Logs", icon: Terminal },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-white border-r border-[#E5E5EA] flex flex-col justify-between h-screen fixed left-0 top-0 z-40 select-none shadow-xs">
      {/* Brand Header */}
      <div className="p-5 border-b border-[#E5E5EA]/80 bg-white">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#FF6B00] via-[#FF8533] to-[#FFA366] flex items-center justify-center shadow-md shadow-orange-500/20 group-hover:scale-105 transition-transform">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-[#1D1D1F] text-base tracking-tight leading-tight">
              AI Kids Studio
            </h1>
            <p className="text-[10px] text-[#EA580C] font-semibold tracking-wider uppercase">
              Apple Silicon M4 • Local
            </p>
          </div>
        </Link>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-1 bg-white">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive =
            pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                item.highlight
                  ? "bg-gradient-to-r from-[#FF6B00] to-[#EA580C] text-white shadow-md shadow-orange-500/25 hover:opacity-95"
                  : isActive
                  ? "bg-[#FFF7ED] text-[#C2410C] font-semibold border border-[#FED7AA] shadow-xs"
                  : "text-[#6E6E73] hover:text-[#1D1D1F] hover:bg-[#F5F5F7]"
              }`}
            >
              <Icon
                className={`w-4 h-4 ${
                  item.highlight
                    ? "text-white"
                    : isActive
                    ? "text-[#EA580C]"
                    : "text-[#86868B]"
                }`}
              />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer / System Health */}
      <div className="p-3 border-t border-[#E5E5EA] bg-[#FAFAFC]">
        <HealthStatus />
      </div>
    </aside>
  );
}
