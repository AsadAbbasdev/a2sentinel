import type { Metadata } from "next";
import { Toaster } from "react-hot-toast";
import Navbar from "@/components/layout/Navbar";
import "./globals.css";

export const metadata: Metadata = {
  title: "A2 Sentinel — AI Security Scanner",
  description: "AI-powered security scanning. Find vulnerabilities before hackers do.",
  keywords: ["security scanner", "vulnerability detection", "AI security", "code security"],
  openGraph: {
    title: "A2 Sentinel — AI Security Scanner",
    description: "Paste your code. AI thinks like a hacker. Free to start.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main className="pt-16 min-h-screen">
          {children}
        </main>
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: "var(--bg-card)",
              color: "var(--text-primary)",
              border: "1px solid var(--border)",
              borderRadius: "10px",
              fontSize: "14px",
            },
            success: { iconTheme: { primary: "#6366f1", secondary: "white" } },
            error: { iconTheme: { primary: "#ef4444", secondary: "white" } },
          }}
        />
      </body>
    </html>
  );
}
