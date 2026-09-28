import type { Metadata, Viewport } from "next";
import { Sidebar } from "@/components/Sidebar";
import { PwaRegister } from "@/components/PwaRegister";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Kids Video Studio",
  description: "Local-first 3D Kids Animation & Song Video Studio for Apple Silicon M4",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "MotionStoryLab",
  },
  icons: {
    icon: "/icon-192.png",
    apple: "/apple-touch-icon.png",
  },
};

export const viewport: Viewport = {
  themeColor: "#FF6B00",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full antialiased">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
      </head>
      <body className="min-h-full bg-[#F5F5F7] text-[#1D1D1F] flex">
        <PwaRegister />
        <Sidebar />
        <div className="ml-64 flex-1 min-h-screen flex flex-col bg-[#F5F5F7]">
          {children}
        </div>
      </body>
    </html>
  );
}
