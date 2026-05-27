"""
A2 Sentinel — Scan Schemas
Pydantic models for all scan-related requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ─── Enums ──────────────────────────────────────────────────────

class SeverityLevel(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    info = "info"


class RiskLevel(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class ScanStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


# ─── Sub-models ─────────────────────────────────────────────────

class Vulnerability(BaseModel):
    id: str
    title: str
    severity: SeverityLevel
    description: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    owasp_category: Optional[str] = None
    cwe_id: Optional[str] = None
    recommendation: str
    references: Optional[List[str]] = []


class AttackStep(BaseModel):
    step: int
    action: str
    payload: Optional[str] = None
    expected_result: str


class AttackSimulation(BaseModel):
    vulnerability_id: str
    attack_name: str
    attack_steps: List[AttackStep]
    impact: str
    proof_of_concept: Optional[str] = None
    cvss_score: Optional[float] = None


class CodeFix(BaseModel):
    fixed_code: str
    changes_made: List[str]
    explanation: str
    additional_recommendations: Optional[List[str]] = []


class VulnerabilitySummary(BaseModel):
    total: int
    critical: int
    high: int
    medium: int
    low: int
    info: int


# ─── Request Schemas ────────────────────────────────────────────

class ScanRequest(BaseModel):
    code: str = Field(..., min_length=10, description="Source code to analyze")
    language: Optional[str] = Field(
        None, description="Programming language: python, javascript, php, java, etc."
    )
    filename: Optional[str] = Field(None, description="Original filename (helps detect language)")
    include_simulation: bool = Field(
        False, description="Run attack simulation on found vulnerabilities"
    )
    include_fix: bool = Field(
        False, description="Generate secure fixed version of the code"
    )


class SimulateRequest(BaseModel):
    code: str = Field(..., min_length=10)
    language: Optional[str] = None
    target_vulnerability: Optional[str] = Field(
        None, description="Focus on specific vuln type e.g. 'sql_injection'"
    )


class FixRequest(BaseModel):
    code: str = Field(..., min_length=10)
    language: Optional[str] = None
    vulnerability_id: Optional[str] = None
    context: Optional[str] = Field(
        None, description="Additional context about the codebase"
    )


# ─── Response Schemas ───────────────────────────────────────────

class ScanResponse(BaseModel):
    scan_id: str
    status: ScanStatus
    security_score: float = Field(..., ge=0, le=100, description="0=insecure, 100=perfectly secure")
    risk_level: RiskLevel
    summary: str
    vulnerability_summary: VulnerabilitySummary
    vulnerabilities: List[Vulnerability]
    simulations: Optional[List[AttackSimulation]] = None
    fix: Optional[CodeFix] = None
    scan_duration_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ScanHistoryItem(BaseModel):
    id: str
    status: str
    security_score: Optional[float]
    risk_level: Optional[str]
    summary: Optional[str]
    language: Optional[str]
    filename: Optional[str]
    total_vulnerabilities: int
    critical_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class ScanHistoryResponse(BaseModel):
    total: int
    page: int
    per_page: int
    scans: List[ScanHistoryItem]
