"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Shield, Clock, AlertTriangle, CheckCircle,
  ChevronRight, Zap
} from "lucide-react";
import toast from "react-hot-toast";
import { scanAPI } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import { ScanHistoryItem } from "@/types";

const RISK_COLORS: Record<string, string> = {
  critical: "#ef4444",
  high: "#f97316",
  medium: "#eab308",
  low: "#22c55e",
};

const SCORE_COLOR = (score: number) => {
  if (score >= 80) return "#22c55e";
  if (score >= 60) return "#eab308";
  if (score >= 40) return "#f97316";
  return "#ef4444";
};

export default function HistoryPage() {
  const router = useRouter();
  const { isAuthenticated, loadFromStorage } = useAuthStore();
  const [scans, setScans] = useState<ScanHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    loadFromStorage();
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    fetchHistory();
  }, [isAuthenticated, page]);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await scanAPI.history(page, 10);
      setScans(res.data.scans);
      setTotal(res.data.total);
    } catch {
      toast.error("Failed to load scan history");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      month: "short", day: "numeric", year: "numeric",
      hour: "2-digit", minute: "2-digit",
    });
  };

  return (
    <div className="min-h-screen px-4 py-8" style={{ background: "var(--bg-primary)" }}>
      <div className="max-w-4xl mx-auto">

        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold">Scan History</h1>
            <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
              {total} total scans
            </p>
          </div>
          <Link href="/scanner"
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all hover:opacity-90"
            style={{ background: "linear-gradient(135deg, #6366f1, #a855f7)", color: "white" }}>
            <Zap className="w-4 h-4" />
            New Scan
          </Link>
        </div>

        {/* List */}
        {loading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="p-5 rounded-xl animate-pulse"
                style={{ background: "var(--bg-card)", border: "1px solid var(--border)", height: "80px" }} />
            ))}
          </div>
        ) : scans.length === 0 ? (
          <div className="text-center py-20 rounded-xl"
            style={{ border: "1px dashed var(--border)" }}>
            <Shield className="w-16 h-16 mx-auto mb-4 opacity-20" />
            <p className="text-lg font-medium mb-2" style={{ color: "var(--text-secondary)" }}>
              No scans yet
            </p>
            <p className="text-sm mb-6" style={{ color: "var(--text-muted)" }}>
              Run your first security scan to see results here
            </p>
            <Link href="/scanner"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl font-medium text-sm"
              style={{ background: "linear-gradient(135deg, #6366f1, #a855f7)", color: "white" }}>
              <Zap className="w-4 h-4" />
              Start Scanning
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {scans.map((scan) => (
              <div key={scan.id}
                className="p-5 rounded-xl transition-all hover:scale-[1.01] cursor-pointer"
                style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
                <div className="flex items-center gap-4">

                  {/* Score Circle */}
                  <div className="w-14 h-14 rounded-xl flex flex-col items-center justify-center flex-shrink-0"
                    style={{
                      background: `${SCORE_COLOR(scan.security_score || 0)}15`,
                      border: `1px solid ${SCORE_COLOR(scan.security_score || 0)}30`,
                    }}>
                    <span className="text-lg font-bold" style={{ color: SCORE_COLOR(scan.security_score || 0) }}>
                      {scan.security_score ?? "?"}
                    </span>
                    <span className="text-xs" style={{ color: "var(--text-muted)" }}>/100</span>
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      {/* Risk badge */}
                      {scan.risk_level && (
                        <span className="text-xs px-2 py-0.5 rounded font-medium"
                          style={{
                            background: `${RISK_COLORS[scan.risk_level]}20`,
                            color: RISK_COLORS[scan.risk_level],
                            border: `1px solid ${RISK_COLORS[scan.risk_level]}40`,
                          }}>
                          {scan.risk_level.toUpperCase()}
                        </span>
                      )}
                      {scan.language && (
                        <span className="text-xs px-2 py-0.5 rounded font-mono"
                          style={{ background: "var(--bg-hover)", color: "var(--text-muted)" }}>
                          {scan.language}
                        </span>
                      )}
                    </div>

                    <p className="text-sm truncate" style={{ color: "var(--text-secondary)" }}>
                      {scan.summary || "Security scan completed"}
                    </p>

                    <div className="flex items-center gap-4 mt-2">
                      <div className="flex items-center gap-1 text-xs" style={{ color: "var(--text-muted)" }}>
                        <Clock className="w-3 h-3" />
                        {formatDate(scan.created_at)}
                      </div>

                      {/* Vuln counts */}
                      {scan.total_vulnerabilities > 0 && (
                        <div className="flex items-center gap-1 text-xs text-red-400">
                          <AlertTriangle className="w-3 h-3" />
                          {scan.critical_count > 0 && `${scan.critical_count} critical`}
                          {scan.critical_count === 0 && `${scan.total_vulnerabilities} issues`}
                        </div>
                      )}

                      {scan.total_vulnerabilities === 0 && (
                        <div className="flex items-center gap-1 text-xs text-green-400">
                          <CheckCircle className="w-3 h-3" />
                          Clean
                        </div>
                      )}
                    </div>
                  </div>

                  <ChevronRight className="w-4 h-4 flex-shrink-0" style={{ color: "var(--text-muted)" }} />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {total > 10 && (
          <div className="flex items-center justify-center gap-3 mt-8">
            <button onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 rounded-lg text-sm disabled:opacity-40 transition-all"
              style={{ background: "var(--bg-card)", border: "1px solid var(--border)", color: "var(--text-primary)" }}>
              Previous
            </button>
            <span className="text-sm" style={{ color: "var(--text-muted)" }}>
              Page {page} of {Math.ceil(total / 10)}
            </span>
            <button onClick={() => setPage(p => p + 1)}
              disabled={page >= Math.ceil(total / 10)}
              className="px-4 py-2 rounded-lg text-sm disabled:opacity-40 transition-all"
              style={{ background: "var(--bg-card)", border: "1px solid var(--border)", color: "var(--text-primary)" }}>
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
