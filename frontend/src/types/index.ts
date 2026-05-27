// ─── Auth Types ─────────────────────────────────────────────────
export interface User {
  id: string;
  email: string;
  full_name: string | null;
  company: string | null;
  plan: string;
  scans_used: number;
  scans_limit: number;
  is_verified: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
  company?: string;
}

// ─── Scan Types ──────────────────────────────────────────────────
export type SeverityLevel = "critical" | "high" | "medium" | "low" | "info";
export type RiskLevel = "critical" | "high" | "medium" | "low";
export type ScanStatus = "pending" | "running" | "completed" | "failed";

export interface Vulnerability {
  id: string;
  title: string;
  severity: SeverityLevel;
  description: string;
  line_number: number | null;
  code_snippet: string | null;
  owasp_category: string | null;
  cwe_id: string | null;
  recommendation: string;
  references: string[];
}

export interface AttackStep {
  step: number;
  action: string;
  payload: string | null;
  expected_result: string;
}

export interface AttackSimulation {
  vulnerability_id: string;
  attack_name: string;
  attack_steps: AttackStep[];
  impact: string;
  proof_of_concept: string | null;
  cvss_score: number | null;
}

export interface CodeFix {
  fixed_code: string;
  changes_made: string[];
  explanation: string;
  additional_recommendations: string[];
}

export interface VulnerabilitySummary {
  total: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
}

export interface ScanResponse {
  scan_id: string;
  status: ScanStatus;
  security_score: number;
  risk_level: RiskLevel;
  summary: string;
  vulnerability_summary: VulnerabilitySummary;
  vulnerabilities: Vulnerability[];
  simulations: AttackSimulation[] | null;
  fix: CodeFix | null;
  scan_duration_ms: number | null;
  created_at: string;
}

export interface ScanRequest {
  code: string;
  language?: string;
  filename?: string;
  include_simulation: boolean;
  include_fix: boolean;
}

export interface ScanHistoryItem {
  id: string;
  status: string;
  security_score: number | null;
  risk_level: string | null;
  summary: string | null;
  language: string | null;
  filename: string | null;
  total_vulnerabilities: number;
  critical_count: number;
  created_at: string;
}

// ─── API Error ───────────────────────────────────────────────────
export interface APIError {
  detail: string;
}
