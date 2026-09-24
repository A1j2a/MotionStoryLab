"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function CreateRedirectPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/");
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-[60vh] text-center p-8">
      <div className="space-y-3">
        <div className="w-10 h-10 border-4 border-[#FF6B00] border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="text-sm font-semibold text-[#1D1D1F]">Opening Unified Studio Dashboard...</p>
      </div>
    </div>
  );
}
