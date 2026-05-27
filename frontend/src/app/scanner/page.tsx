"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Shield, Zap, Bug, Terminal, ChevronDown, Loader2,
  AlertTriangle, CheckCircle, Upload, X, FileCode, Lock
} from "lucide-react";
import toast from "react-hot-toast";
import { scanAPI } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import { ScanResponse, Vulnerability, SeverityLevel } from "@/types";

const LANGUAGES = [
  "Auto Detect", "python", "javascript", "typescript", "php",
  "java", "go", "ruby", "rust", "sql", "bash", "cpp", "csharp"
];

const FILE_EXTENSIONS: Record<string, string> = {
  ".py": "python", ".js": "javascript", ".ts": "typescript",
  ".jsx": "javascript", ".tsx": "typescript", ".php": "php",
  ".java": "java", ".go": "go", ".rb": "ruby", ".rs": "rust",
  ".sql": "sql", ".sh": "bash", ".cpp": "cpp", ".cs": "csharp",
  ".c": "cpp", ".kt": "java",
};

const SEVERITY_CONFIG: Record<SeverityLevel, { color: string; bg: string; label: string }> = {
  critical: { color: "#ef4444", bg: "rgba(239,68,68,0.1)", label: "CRITICAL" },
  high: { color: "#f97316", bg: "rgba(249,115,22,0.1)", label: "HIGH" },
  medium: { color: "#eab308", bg: "rgba(234,179,8,0.1)", label: "MEDIUM" },
  low: { color: "#22c55e", bg: "rgba(34,197,94,0.1)", label: "LOW" },
  info: { color: "#3b82f6", bg: "rgba(59,130,246,0.1)", label: "INFO" },
};

const SCORE_CONFIG = (score: number) => {
  if (score >= 80) return { color: "#22c55e", label: "SECURE", emoji: "✅" };
  if (score >= 60) return { color: "#eab308", label: "MODERATE RISK", emoji: "⚠️" };
  if (score >= 40) return { color: "#f97316", label: "HIGH RISK", emoji: "🔴" };
  return { color: "#ef4444", label: "CRITICAL RISK", emoji: "💀" };
};

export default function ScannerPage() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
  setMounted(true);
  }, []);
  const { isAuthenticated } = useAuthStore();
  const authReady = mounted && isAuthenticated;
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dropZoneRef = useRef<HTMLDivElement>(null);

  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("Auto Detect");
  const [includeSimulation, setIncludeSimulation] = useState(false);
  const [includeFix, setIncludeFix] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResponse | null>(null);
  const [activeVuln, setActiveVuln] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"vulnerabilities" | "simulation" | "fix">("vulnerabilities");
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const [isGuest, setIsGuest] = useState(false);

  // ─── File Upload ──────────────────────────────────────────────
  const handleFile = useCallback((file: File) => {
    // Check file size (max 500KB)
    if (file.size > 500 * 1024) {
      toast.error("File too large. Max 500KB allowed.");
      return;
    }

    // Check extension
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    const supportedExts = Object.keys(FILE_EXTENSIONS);
    if (!supportedExts.includes(ext)) {
      toast.error(`Unsupported file type. Supported: ${supportedExts.join(", ")}`);
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setCode(content);
      setUploadedFile(file.name);

      // Auto detect language
      const detectedLang = FILE_EXTENSIONS[ext];
      if (detectedLang) {
        setLanguage(detectedLang);
        toast.success(`File loaded: ${file.name} (${detectedLang})`);
      }
    };
    reader.readAsText(file);
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  };

  const clearFile = () => {
    setUploadedFile(null);
    setCode("");
    setLanguage("Auto Detect");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // ─── Scan ─────────────────────────────────────────────────────
  const handleScan = async () => {
    if (!code.trim() || code.trim().length < 10) {
      toast.error("Please paste your code or upload a file first");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      let res;

      if (authReady) {
        // Logged in user — full scan
        setIsGuest(false);
        res = await scanAPI.scan({
          code,
          language: language === "Auto Detect" ? undefined : language,
          include_simulation: includeSimulation,
          include_fix: includeFix,
        });
      } else {
        // Guest — free demo scan
        setIsGuest(true);
        res = await scanAPI.guestScan({
          code,
          language: language === "Auto Detect" ? undefined : language,
        });
      }

      setResult(res.data);
      setActiveTab("vulnerabilities");

      const total = res.data.vulnerability_summary?.total || 0;
      const critical = res.data.vulnerability_summary?.critical || 0;

      if (total === 0) {
        toast.success("No vulnerabilities found! Code looks clean 🎉");
      } else if (critical > 0) {
        toast.error(`Found ${critical} critical vulnerabilities!`);
      } else {
        toast(`Found ${total} vulnerabilities`, { icon: "⚠️" });
      }
    } catch (err: any) {
      const msg = err.response?.data?.detail || "Scan failed";
      if (err.response?.status === 429) {
        toast.error("Scan limit reached. Upgrade your plan.");
      } else {
        toast.error(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen" style={{ background: "var(--bg-primary)" }}>
      <div className="max-w-7xl mx-auto px-4 py-8">

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">
            <span className="gradient-text">AI Security Scanner</span>
          </h1>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            Paste your code or upload a file — AI finds vulnerabilities in seconds
          </p>
          {!authReady && (
            <div className="inline-flex items-center gap-2 mt-3 px-4 py-2 rounded-full text-sm"
              style={{ background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.3)", color: "#818cf8" }}>
              <Zap className="w-3.5 h-3.5" />
              Free demo scan — no login required
            </div>
          )}
        </div>

        <div className="grid lg:grid-cols-2 gap-6">

          {/* Left — Input */}
          <div className="flex flex-col gap-4">

            {/* Toolbar */}
            <div className="flex items-center gap-3 flex-wrap">
              {/* Language */}
              <div className="relative">
                <select value={language} onChange={(e) => setLanguage(e.target.value)}
                  className="appearance-none pl-3 pr-8 py-2 rounded-lg text-sm outline-none cursor-pointer"
                  style={{ background: "var(--bg-card)", border: "1px solid var(--border)", color: "var(--text-primary)" }}>
                  {LANGUAGES.map((l) => <option key={l} value={l}>{l}</option>)}
                </select>
                <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none"
                  style={{ color: "var(--text-muted)" }} />
              </div>

              {/* Upload button */}
              <button onClick={() => fileInputRef.current?.click()}
                className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all hover:opacity-80"
                style={{ background: "var(--bg-card)", border: "1px solid var(--border)", color: "var(--text-secondary)" }}>
                <Upload className="w-4 h-4" />
                Upload File
              </button>
              <input ref={fileInputRef} type="file"
                accept=".py,.js,.ts,.jsx,.tsx,.php,.java,.go,.rb,.rs,.sql,.sh,.cpp,.cs,.c,.kt"
                onChange={handleFileInput} className="hidden" />

              {/* Uploaded file badge */}
              {uploadedFile && (
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs"
                  style={{ background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.3)", color: "#818cf8" }}>
                  <FileCode className="w-3.5 h-3.5" />
                  {uploadedFile}
                  <button onClick={clearFile} className="hover:text-red-400 transition-colors">
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}

              {/* Simulation toggle — only for logged in */}
              {authReady && (
                <>
                  <label className="flex items-center gap-2 cursor-pointer text-sm"
                    style={{ color: "var(--text-secondary)" }}>
                    <div className="w-8 h-4 rounded-full relative transition-colors"
                      style={{ background: includeSimulation ? "#6366f1" : "var(--border)" }}
                      onClick={() => setIncludeSimulation(!includeSimulation)}>
                      <div className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-transform ${includeSimulation ? "translate-x-4" : "translate-x-0.5"}`} />
                    </div>
                    Attack Sim
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer text-sm"
                    style={{ color: "var(--text-secondary)" }}>
                    <div className="w-8 h-4 rounded-full relative transition-colors"
                      style={{ background: includeFix ? "#6366f1" : "var(--border)" }}
                      onClick={() => setIncludeFix(!includeFix)}>
                      <div className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-transform ${includeFix ? "translate-x-4" : "translate-x-0.5"}`} />
                    </div>
                    Auto Fix
                  </label>
                </>
              )}
            </div>

            {/* Drop Zone + Code Editor */}
            <div
              ref={dropZoneRef}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className="relative rounded-xl overflow-hidden flex-1 transition-all"
              style={{
                border: isDragging
                  ? "2px dashed #6366f1"
                  : "1px solid var(--border)",
                minHeight: "400px",
                background: isDragging ? "rgba(99,102,241,0.05)" : "transparent",
              }}>

              {/* Drag overlay */}
              {isDragging && (
                <div className="absolute inset-0 flex flex-col items-center justify-center z-10"
                  style={{ background: "rgba(99,102,241,0.1)" }}>
                  <Upload className="w-12 h-12 mb-3" style={{ color: "#6366f1" }} />
                  <p className="font-semibold" style={{ color: "#6366f1" }}>Drop your file here</p>
                </div>
              )}

              {/* Editor header */}
              <div className="flex items-center gap-2 px-4 py-2 border-b"
                style={{ background: "var(--bg-card)", borderColor: "var(--border)" }}>
                <div className="w-3 h-3 rounded-full bg-red-500/70" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
                <div className="w-3 h-3 rounded-full bg-green-500/70" />
                <span className="ml-2 text-xs font-mono" style={{ color: "var(--text-muted)" }}>
                  {uploadedFile || (language === "Auto Detect" ? "code.txt" : `code.${language === "python" ? "py" : language === "javascript" ? "js" : language}`)}
                </span>
                {!uploadedFile && !code && (
                  <span className="ml-auto text-xs" style={{ color: "var(--text-muted)" }}>
                    drag & drop or paste code
                  </span>
                )}
              </div>

              <textarea
                value={code}
                onChange={(e) => { setCode(e.target.value); setUploadedFile(null); }}
                placeholder={`# Paste your code here or drag & drop a file...\n\ndef get_user(user_id):\n    query = "SELECT * FROM users WHERE id = " + user_id\n    cursor.execute(query)\n    return cursor.fetchone()`}
                className="w-full p-4 font-mono text-sm resize-none outline-none"
                style={{
                  background: "var(--bg-primary)",
                  color: "var(--text-primary)",
                  minHeight: "360px",
                  lineHeight: "1.6",
                }}
              />
            </div>

            {/* Scan Button */}
            <button onClick={handleScan} disabled={loading}
              className="w-full py-4 rounded-xl font-semibold text-base transition-all hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
              style={{ background: "linear-gradient(135deg, #6366f1, #a855f7)", color: "white" }}>
              {loading ? (
                <><Loader2 className="w-5 h-5 animate-spin" /> Scanning...</>
              ) : (
                <><Shield className="w-5 h-5" />
                  {authReady ? "Scan for Vulnerabilities" : "🚀 Free Demo Scan"}</>
              )}
            </button>

            {/* Guest CTA */}
            {!authReady && (
              <div className="p-4 rounded-xl text-center"
                style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
                <p className="text-sm mb-3" style={{ color: "var(--text-secondary)" }}>
                  🔓 Sign up free to unlock attack simulation, auto-fix, and unlimited scans
                </p>
                <div className="flex gap-3 justify-center">
                  <button onClick={() => router.push("/register")}
                    className="px-4 py-2 rounded-lg text-sm font-medium transition-all hover:opacity-90"
                    style={{ background: "linear-gradient(135deg, #6366f1, #a855f7)", color: "white" }}>
                    Create Free Account
                  </button>
                  <button onClick={() => router.push("/login")}
                    className="px-4 py-2 rounded-lg text-sm transition-all"
                    style={{ background: "var(--bg-hover)", border: "1px solid var(--border)", color: "var(--text-primary)" }}>
                    Login
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Right — Results */}
          <div>
            {!result && !loading && (
              <div className="h-full flex flex-col items-center justify-center text-center p-8 rounded-xl"
                style={{ border: "1px dashed var(--border)", minHeight: "400px" }}>
                <Shield className="w-16 h-16 mb-4 opacity-20" />
                <p className="text-lg font-medium mb-2" style={{ color: "var(--text-secondary)" }}>
                  Ready to Scan
                </p>
                <p className="text-sm mb-4" style={{ color: "var(--text-muted)" }}>
                  Paste code or upload a file
                </p>
                <div className="flex flex-wrap justify-center gap-2">
                  {[".py", ".js", ".ts", ".php", ".java", ".go"].map((ext) => (
                    <span key={ext} className="px-2 py-1 rounded text-xs font-mono"
                      style={{ background: "var(--bg-card)", border: "1px solid var(--border)", color: "var(--text-muted)" }}>
                      {ext}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {loading && (
              <div className="h-full flex flex-col items-center justify-center text-center p-8 rounded-xl"
                style={{ border: "1px solid var(--border)", minHeight: "400px" }}>
                <div className="relative mb-6">
                  <div className="w-20 h-20 rounded-full border-4 border-indigo-500/20 animate-spin"
                    style={{ borderTopColor: "#6366f1" }} />
                  <Shield className="absolute inset-0 m-auto w-8 h-8" style={{ color: "#6366f1" }} />
                </div>
                <p className="font-medium mb-1">AI is analyzing your code...</p>
                <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                  OWASP Top 10 + AI deep analysis
                </p>
              </div>
            )}

            {result && (
              <div className="flex flex-col gap-4 animate-fade-in">

                {/* Score Card */}
                <div className="p-6 rounded-xl" style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <div className="text-sm mb-1" style={{ color: "var(--text-muted)" }}>Security Score</div>
                      <div className="text-5xl font-bold" style={{ color: SCORE_CONFIG(result.security_score).color }}>
                        {result.security_score}<span className="text-2xl">/100</span>
                      </div>
                      <div className="text-sm font-medium mt-1" style={{ color: SCORE_CONFIG(result.security_score).color }}>
                        {SCORE_CONFIG(result.security_score).emoji} {SCORE_CONFIG(result.security_score).label}
                      </div>
                    </div>
                    <div className="flex flex-col gap-1 text-right">
                      {result.vulnerability_summary && Object.entries(result.vulnerability_summary)
                        .filter(([k]) => k !== "total")
                        .map(([key, val]) => (
                          val > 0 && (
                            <div key={key} className="flex items-center gap-2 justify-end text-sm">
                              <span style={{ color: SEVERITY_CONFIG[key as SeverityLevel]?.color }}>
                                {val} {key}
                              </span>
                            </div>
                          )
                        ))}
                      <div className="text-sm font-semibold mt-1">
                        {result.vulnerability_summary?.total} total
                      </div>
                    </div>
                  </div>
                  <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>
                    {result.summary}
                  </p>
                  <div className="mt-3 text-xs" style={{ color: "var(--text-muted)" }}>
                    Scanned in {result.scan_duration_ms}ms
                  </div>
                </div>

                {/* Guest upgrade banner */}
                {isGuest && (
                  <div className="p-4 rounded-xl flex items-center gap-4"
                    style={{ background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.3)" }}>
                    <Lock className="w-8 h-8 flex-shrink-0" style={{ color: "#6366f1" }} />
                    <div className="flex-1">
                      <p className="text-sm font-medium" style={{ color: "#818cf8" }}>
                        Sign up to unlock full results
                      </p>
                      <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
                        Attack simulation, auto-fix, full vulnerability list & more
                      </p>
                    </div>
                    <button onClick={() => router.push("/register")}
                      className="px-3 py-2 rounded-lg text-sm font-medium flex-shrink-0"
                      style={{ background: "linear-gradient(135deg, #6366f1, #a855f7)", color: "white" }}>
                      Sign Up Free
                    </button>
                  </div>
                )}

                {/* Tabs */}
                <div className="flex gap-2 flex-wrap">
                  {[
                    { key: "vulnerabilities", label: `Vulnerabilities (${result.vulnerability_summary?.total || 0})`, icon: Bug },
                    result.simulations && { key: "simulation", label: "Attack Sim", icon: Terminal },
                    result.fix && { key: "fix", label: "Auto Fix", icon: CheckCircle },
                  ].filter(Boolean).map((tab: any) => (
                    <button key={tab.key} onClick={() => setActiveTab(tab.key)}
                      className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm transition-all"
                      style={{
                        background: activeTab === tab.key ? "#6366f1" : "var(--bg-card)",
                        color: activeTab === tab.key ? "white" : "var(--text-secondary)",
                        border: "1px solid var(--border)",
                      }}>
                      <tab.icon className="w-3.5 h-3.5" />
                      {tab.label}
                    </button>
                  ))}
                </div>

                {/* Vulnerabilities */}
                {activeTab === "vulnerabilities" && (
                  <div className="flex flex-col gap-3 max-h-96 overflow-y-auto pr-1">
                    {result.vulnerabilities.length === 0 ? (
                      <div className="p-6 rounded-xl text-center"
                        style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
                        <CheckCircle className="w-12 h-12 mx-auto mb-3" style={{ color: "#22c55e" }} />
                        <p className="font-medium">No vulnerabilities found!</p>
                      </div>
                    ) : (
                      result.vulnerabilities.map((vuln) => (
                        <VulnerabilityCard key={vuln.id} vuln={vuln}
                          isActive={activeVuln === vuln.id}
                          onToggle={() => setActiveVuln(activeVuln === vuln.id ? null : vuln.id)}
                        />
                      ))
                    )}

                    {/* Guest — locked results */}
                    {isGuest && result.vulnerability_summary?.total > 5 && (
                      <div className="p-4 rounded-xl text-center cursor-pointer"
                        style={{ background: "var(--bg-card)", border: "1px dashed var(--border)" }}
                        onClick={() => router.push("/register")}>
                        <Lock className="w-6 h-6 mx-auto mb-2" style={{ color: "var(--text-muted)" }} />
                        <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                          +{result.vulnerability_summary.total - 5} more vulnerabilities hidden
                        </p>
                        <p className="text-xs mt-1" style={{ color: "#6366f1" }}>
                          Sign up free to see all →
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* Simulation */}
                {activeTab === "simulation" && result.simulations && (
                  <div className="flex flex-col gap-3 max-h-96 overflow-y-auto pr-1">
                    {result.simulations.map((sim, i) => (
                      <div key={i} className="p-4 rounded-xl"
                        style={{ background: "var(--bg-card)", border: "1px solid rgba(239,68,68,0.3)" }}>
                        <div className="flex items-center gap-2 mb-3">
                          <AlertTriangle className="w-4 h-4 text-red-400" />
                          <span className="font-medium text-red-400">{sim.attack_name}</span>
                          {sim.cvss_score && (
                            <span className="ml-auto text-xs px-2 py-0.5 rounded"
                              style={{ background: "rgba(239,68,68,0.2)", color: "#ef4444" }}>
                              CVSS {sim.cvss_score}/10
                            </span>
                          )}
                        </div>
                        <div className="space-y-2 mb-3">
                          {sim.attack_steps.map((step) => (
                            <div key={step.step} className="text-sm p-2 rounded"
                              style={{ background: "var(--bg-primary)" }}>
                              <span className="text-indigo-400 font-mono">Step {step.step}:</span>{" "}
                              <span style={{ color: "var(--text-secondary)" }}>{step.action}</span>
                              {step.payload && (
                                <div className="mt-1 font-mono text-xs p-1.5 rounded"
                                  style={{ background: "rgba(0,0,0,0.3)", color: "#f97316" }}>
                                  {step.payload}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                          <span className="text-red-400 font-medium">Impact: </span>{sim.impact}
                        </p>
                      </div>
                    ))}
                  </div>
                )}

                {/* Fix */}
                {activeTab === "fix" && result.fix && (
                  <div className="p-4 rounded-xl"
                    style={{ background: "var(--bg-card)", border: "1px solid rgba(34,197,94,0.3)" }}>
                    <div className="flex items-center gap-2 mb-3">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      <span className="font-medium text-green-400">Secure Fixed Code</span>
                    </div>
                    <pre className="text-xs font-mono p-3 rounded overflow-x-auto max-h-48"
                      style={{ background: "var(--bg-primary)", color: "var(--text-primary)" }}>
                      {result.fix.fixed_code}
                    </pre>
                    <div className="mt-3">
                      <p className="text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>
                        Changes made:
                      </p>
                      <ul className="space-y-1">
                        {result.fix.changes_made.map((change, i) => (
                          <li key={i} className="text-sm flex gap-2" style={{ color: "var(--text-secondary)" }}>
                            <span className="text-green-400">✓</span> {change}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Vulnerability Card ──────────────────────────────────────────
function VulnerabilityCard({ vuln, isActive, onToggle }: {
  vuln: Vulnerability;
  isActive: boolean;
  onToggle: () => void;
}) {
  const config = SEVERITY_CONFIG[vuln.severity] || SEVERITY_CONFIG.info;

  return (
    <div className="rounded-xl overflow-hidden cursor-pointer transition-all"
      style={{ background: "var(--bg-card)", border: `1px solid ${config.color}40` }}
      onClick={onToggle}>
      <div className="p-4">
        <div className="flex items-start gap-3">
          <span className="px-2 py-0.5 rounded text-xs font-bold flex-shrink-0"
            style={{ background: config.bg, color: config.color, border: `1px solid ${config.color}40` }}>
            {config.label}
          </span>
          <div className="flex-1 min-w-0">
            <p className="font-medium text-sm">{vuln.title}</p>
            {vuln.line_number && (
              <p className="text-xs mt-0.5 font-mono" style={{ color: "var(--text-muted)" }}>
                Line {vuln.line_number}
              </p>
            )}
          </div>
          <ChevronDown className={`w-4 h-4 flex-shrink-0 transition-transform ${isActive ? "rotate-180" : ""}`}
            style={{ color: "var(--text-muted)" }} />
        </div>
      </div>

      {isActive && (
        <div className="px-4 pb-4 space-y-3 animate-fade-in">
          {vuln.code_snippet && (
            <div className="font-mono text-xs p-3 rounded"
              style={{ background: "var(--bg-primary)", color: "#f97316" }}>
              {vuln.code_snippet}
            </div>
          )}
          <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>
            {vuln.description}
          </p>
          <div className="p-3 rounded"
            style={{ background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.2)" }}>
            <p className="text-xs font-medium mb-1" style={{ color: "#6366f1" }}>Recommendation</p>
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>{vuln.recommendation}</p>
          </div>
          <div className="flex gap-4 text-xs" style={{ color: "var(--text-muted)" }}>
            {vuln.owasp_category && <span>📋 {vuln.owasp_category}</span>}
            {vuln.cwe_id && <span>🔗 {vuln.cwe_id}</span>}
          </div>
        </div>
      )}
    </div>
  );
}
