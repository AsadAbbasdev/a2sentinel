"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Shield, LogOut, User, History, Zap } from "lucide-react";
import { useAuthStore } from "@/store/authStore";

export default function Navbar() {
  const router = useRouter();
  const { user, isAuthenticated, logout, loadFromStorage } = useAuthStore();

  useEffect(() => {
    loadFromStorage();
  }, []);

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b"
      style={{ background: "rgba(10,10,15,0.9)", backdropFilter: "blur(12px)", borderColor: "var(--border)" }}>
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">

        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: "linear-gradient(135deg, #6366f1, #a855f7)" }}>
            <Shield className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-lg" style={{ color: "var(--text-primary)" }}>
            A2 <span className="gradient-text">Sentinel</span>
          </span>
        </Link>

        {/* Nav Links */}
        <div className="hidden md:flex items-center gap-6">
          <Link href="/scanner" className="text-sm flex items-center gap-1.5 transition-colors hover:text-indigo-400"
            style={{ color: "var(--text-secondary)" }}>
            <Zap className="w-4 h-4" /> Scanner
          </Link>
          {isAuthenticated && (
            <Link href="/history" className="text-sm flex items-center gap-1.5 transition-colors hover:text-indigo-400"
              style={{ color: "var(--text-secondary)" }}>
              <History className="w-4 h-4" /> History
            </Link>
          )}
        </div>

        {/* Auth */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <>
              {/* Usage badge */}
              <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs"
                style={{ background: "var(--bg-card)", border: "1px solid var(--border)", color: "var(--text-secondary)" }}>
                <div className="w-1.5 h-1.5 rounded-full bg-green-400" />
                {user?.scans_used}/{user?.scans_limit} scans
              </div>

              <Link href="/dashboard"
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors"
                style={{ color: "var(--text-secondary)", background: "var(--bg-card)", border: "1px solid var(--border)" }}>
                <User className="w-3.5 h-3.5" />
                <span className="hidden md:inline">{user?.full_name || user?.email?.split("@")[0]}</span>
              </Link>

              <button onClick={handleLogout}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-all hover:bg-red-500/10 hover:text-red-400"
                style={{ color: "var(--text-muted)", border: "1px solid var(--border)" }}>
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </>
          ) : (
            <>
              <Link href="/login"
                className="text-sm px-4 py-2 rounded-lg transition-colors"
                style={{ color: "var(--text-secondary)" }}>
                Login
              </Link>
              <Link href="/register"
                className="text-sm px-4 py-2 rounded-lg font-medium transition-all hover:opacity-90"
                style={{ background: "linear-gradient(135deg, #6366f1, #a855f7)", color: "white" }}>
                Get Started Free
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
