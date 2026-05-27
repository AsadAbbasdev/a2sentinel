"""
A2 Sentinel — Scan Model
Stores every scan result: code, vulnerabilities, score, report.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, Float, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class Scan(Base):
    __tablename__ = "scans"

    # ─── Identity ───────────────────────────────────────────────
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )

    # ─── Input ──────────────────────────────────────────────────
    code_snippet: Mapped[str] = mapped_column(Text, nullable=True)   # first 5000 chars
    language: Mapped[str] = mapped_column(String(50), nullable=True)
    filename: Mapped[str] = mapped_column(String(500), nullable=True)
    repo_url: Mapped[str] = mapped_column(String(500), nullable=True)

    # ─── Status: pending | running | completed | failed ─────────
    status: Mapped[str] = mapped_column(String(50), default="pending")

    # ─── Scan Type: code_scan | simulation | redteam | fix ──────
    scan_type: Mapped[str] = mapped_column(String(50), default="code_scan")

    # ─── Results ────────────────────────────────────────────────
    vulnerabilities: Mapped[dict] = mapped_column(JSON, nullable=True)
    simulations: Mapped[dict] = mapped_column(JSON, nullable=True)
    suggested_fix: Mapped[dict] = mapped_column(JSON, nullable=True)

    security_score: Mapped[float] = mapped_column(Float, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)

    # ─── Stats ──────────────────────────────────────────────────
    total_vulnerabilities: Mapped[int] = mapped_column(Integer, default=0)
    critical_count: Mapped[int] = mapped_column(Integer, default=0)
    high_count: Mapped[int] = mapped_column(Integer, default=0)
    medium_count: Mapped[int] = mapped_column(Integer, default=0)
    low_count: Mapped[int] = mapped_column(Integer, default=0)
    scan_duration_ms: Mapped[int] = mapped_column(Integer, nullable=True)

    # ─── Timestamps ─────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # ─── Relationships ──────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="scans")

    def __repr__(self):
        return f"<Scan {self.id[:8]} | score={self.security_score} | status={self.status}>"
