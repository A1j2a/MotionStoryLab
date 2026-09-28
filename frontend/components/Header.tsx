"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Film, Download } from "lucide-react";

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export function Header({ title = "Studio Dashboard", subtitle }: HeaderProps) {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [installed, setInstalled] = useState(false);

  useEffect(() => {
    const handleBeforeInstall = (e: any) => {
      e.preventDefault();
      setDeferredPrompt(e);
    };

    const handleAppInstalled = () => {
      setInstalled(true);
      setDeferredPrompt(null);
    };

    window.addEventListener("beforeinstallprompt", handleBeforeInstall);
    window.addEventListener("appinstalled", handleAppInstalled);

    return () => {
      window.removeEventListener("beforeinstallprompt", handleBeforeInstall);
      window.removeEventListener("appinstalled", handleAppInstalled);
    };
  }, []);

  const handleInstallClick = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const choice = await deferredPrompt.userChoice;
      if (choice.outcome === "accepted") {
        setInstalled(true);
      }
      setDeferredPrompt(null);
    }
  };

  return (
    <header className="h-16 border-b border-[#E5E5EA] bg-white/80 backdrop-blur-md sticky top-0 z-30 px-8 flex items-center justify-between">
      <div>
        <h2 className="text-base font-bold text-[#1D1D1F] tracking-tight">{title}</h2>
        {subtitle && (
          <p className="text-xs text-[#6E6E73] font-normal">{subtitle}</p>
        )}
      </div>

      <div className="flex items-center gap-3">
        {deferredPrompt && !installed && (
          <button
            onClick={handleInstallClick}
            className="flex items-center gap-1.5 bg-[#F0FDF4] hover:bg-[#DCFCE7] text-[#16A34A] border border-[#BBF7D0] text-xs font-semibold px-3 py-1.5 rounded-xl transition-all cursor-pointer shadow-xs"
            title="Install as Desktop App"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Install App</span>
          </button>
        )}
        <Link
          href="/create"
          className="flex items-center gap-2 bg-gradient-to-r from-[#FF6B00] to-[#EA580C] hover:opacity-95 text-white text-xs font-semibold px-4 py-2 rounded-xl shadow-md shadow-orange-500/20 transition-all cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>New Video</span>
        </Link>
        <Link
          href="/projects"
          className="flex items-center gap-2 bg-white hover:bg-[#F5F5F7] text-[#1D1D1F] border border-[#E5E5EA] text-xs font-medium px-3.5 py-2 rounded-xl transition-colors shadow-xs"
        >
          <Film className="w-3.5 h-3.5 text-[#EA580C]" />
          <span>Projects</span>
        </Link>
      </div>
    </header>
  );
}
