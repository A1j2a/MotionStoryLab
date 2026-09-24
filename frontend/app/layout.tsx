import type { Metadata } from "next";
import { Sidebar } from "@/components/Sidebar";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Kids Video Studio",
  description: "Local-first 3D Kids Animation & Song Video Studio for Apple Silicon M4",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full bg-[#F5F5F7] text-[#1D1D1F] flex">
        <Sidebar />
        <div className="ml-64 flex-1 min-h-screen flex flex-col bg-[#F5F5F7]">
          {children}
        </div>
      </body>
    </html>
  );
}
