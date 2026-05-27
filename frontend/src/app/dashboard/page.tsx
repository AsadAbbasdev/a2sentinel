"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Shield, Zap, AlertTriangle, CheckCircle,
  TrendingUp, Clock, Key, Copy, RefreshCw
} from "lucide-react";
import toast from "react-hot-toast";
import { userAPI } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";

interface Usage {
  plan: string;
  scans_used: number;
  scans_limit: number;
  scans_remaining: number;
  simulations_used: number;
  api_key: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, loadFromStorage } = useAuthStore();
  const [usage, setUsage] = useState<Usage | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFromStorage();
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    fetchUsage();
  }, [isAuthenticated]);

  const fetchUsage = async () => {
    try {
      const res = await userAPI.usage();
      setUsage(res.data);
    } catch {
      toast.error("Failed to load usage data");
    } finally {
      setLoading(false);
    }
  };

  const copyApiKey = () => {
    if (usage?.api_key) {
      navigator.clipboard.writeText(usage.api_key);
      toast.success("API key copied!");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "var(--bg-primary)" }}>
        <div className="w-8 h-8 rounded-full border-2 border-indigo-500/20 animate-spin" style={{ borderTopColor: "#6366f1" }} />
      </div>
    );
  }

  const usagePercent = usage ? (usage.scans_used / usage.scans_limit) * 100 : 0;

  return (
    <div className="min-h-screen px-4 py-8" style={{ background: "var(--bg-primary)" }}>
      <div className="max-w-5xl mx-auto">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold">
            Welcome back, <span className="gradient-text">{user?.full_name || user?.email?.split("@")[0]}</span>
          </h1>
          <p className="mt-1 text-sm" style={{ color: "var(--text-secondary)" }}>
            {user?.email} · <span className="capitalize">{usage?.plan} plan</span>
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {[
            { label: "Scans Used", value: usage?.scans_used || 0, icon: Shield, color: "#6366f1" },
            { label: "Scans Left", value: usage?.scans_remaining || 0, icon: Zap, color: "#22c55e" },
            { label: "Simulations", value: usage?.simulations_used || 0, icon: AlertTriangle, color: "#f97316" },
            { label: "Plan", value: usage?.plan?.toUpperCase() || "FREE", icon: TrendingUp, color: "#a855f7" },
          ].map((stat) => (
            <div key={stat.label} className="p-4 rounded-xl"
              style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
              <div className="flex items-center gap-2 mb-2">
                <stat.icon className="w-4 h-4" style={{ color: stat.color }} />
                <span className="text-xs" style={{ color: "var(--text-muted)" }}>{stat.label}</span>
              </div>
              <div className="text-2xl font-bold">{stat.value}</div>
            </div>
          ))}
        </div>

        {/* Usage Bar */}
        <div className="p-6 rounded-xl mb-6" style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
          <div className="flex justify-between items-center mb-3">
            <span className="text-sm font-medium">Monthly Scan Usage</span>
            <span className="text-sm" style={{ color: "var(--text-muted)" }}>
              {usage?.scans_used} / {usage?.scans_limit}
            </span>
          </div>
          <div className="w-full h-2 rounded-full" style={{ background: "var(--bg-primary)" }}>
            <div className="h-2 rounded-full transition-all"
              style={{
                width: `${Math.min(usagePercent, 100)}%`,
                background: usagePercent > 80 ? "#ef4444" : usagePercent > 60 ? "#f97316" : "#6366f1",
              }} />
          </div>
          {usagePercent > 80 && (
            <p className="text-xs mt-2 text-red-400">
              Running low! <Link href="/pricing" className="underline">Upgrade your plan</Link>
            </p>
          )}
        </div>

        {/* API Key */}
        <div className="p-6 rounded-xl mb-6" style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
          <div className="flex items-center gap-2 mb-4">
            <Key className="w-4 h-4" style={{ color: "var(--accent)" }} />
            <span className="font-medium">Your API Key</span>
          </div>
          <div className="flex items-center gap-3">
            <code className="flex-1 px-4 py-3 rounded-xl text-sm font-mono truncate"
              style={{ background: "var(--bg-primary)", border: "1px solid var(--border)", color: "var(--text-secondary)" }}>
              {usage?.api_key || "No API key"}
            </code>
            <button onClick={copyApiKey}
              className="p-3 rounded-xl transition-colors hover:bg-indigo-500/10"
              style={{ border: "1px solid var(--border)" }}>
              <Copy className="w-4 h-4" style={{ color: "var(--accent)" }} />
            </button>
          </div>
          <p className="text-xs mt-3" style={{ color: "var(--text-muted)" }}>
            Use this key with <code className="font-mono">X-API-Key</code> header for programmatic access
          </p>

          {/* API Example */}
          <div className="mt-4 p-3 rounded-xl font-mono text-xs overflow-x-auto"
            style={{ background: "var(--bg-primary)", border: "1px solid var(--border)", color: "var(--text-secondary)" }}>
            <div style={{ color: "var(--text-muted)" }}># Scan via curl</div>
            <div className="mt-1">curl -X POST http://localhost:8000/api/scan \</div>
            <div>{"  "}-H "X-API-Key: {usage?.api_key?.slice(0, 20)}..." \</div>
            <div>{"  "}-d '{`{"code": "...", "language": "python"}`}'</div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-2 gap-4">
          <Link href="/scanner"
            className="p-6 rounded-xl flex items-center gap-4 transition-all hover:scale-105 hover:border-indigo-500"
            style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
            <div className="w-12 h-12 rounded-xl flex items-center justify-center"
              style={{ background: "rgba(99,102,241,0.1)" }}>
              <Shield className="w-6 h-6" style={{ color: "#6366f1" }} />
            </div>
            <div>
              <div className="font-medium">Start New Scan</div>
              <div className="text-sm mt-0.5" style={{ color: "var(--text-muted)" }}>
                Scan your code for vulnerabilities
              </div>
            </div>
          </Link>

          <Link href="/history"
            className="p-6 rounded-xl flex items-center gap-4 transition-all hover:scale-105 hover:border-indigo-500"
            style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
            <div className="w-12 h-12 rounded-xl flex items-center justify-center"
              style={{ background: "rgba(168,85,247,0.1)" }}>
              <Clock className="w-6 h-6" style={{ color: "#a855f7" }} />
            </div>
            <div>
              <div className="font-medium">Scan History</div>
              <div className="text-sm mt-0.5" style={{ color: "var(--text-muted)" }}>
                View all previous scans
              </div>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
