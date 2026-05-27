"""
A2 Sentinel — User Model
Stores all user account information, plan, API key, usage stats.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    # ─── Identity ───────────────────────────────────────────────
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)

    # ─── Status ─────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # ─── Plan: free | pro | team | enterprise ───────────────────
    plan: Mapped[str] = mapped_column(String(50), default="free")

    # ─── API Access ─────────────────────────────────────────────
    api_key: Mapped[str] = mapped_column(
        String(80), unique=True, nullable=True, index=True
    )

    # ─── Usage Tracking ─────────────────────────────────────────
    scans_used: Mapped[int] = mapped_column(Integer, default=0)
    scans_limit: Mapped[int] = mapped_column(Integer, default=10)  # free tier default
    simulations_used: Mapped[int] = mapped_column(Integer, default=0)

    # ─── Profile ────────────────────────────────────────────────
    company: Mapped[str] = mapped_column(String(255), nullable=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)

    # ─── Timestamps ─────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_login_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # ─── Relationships ──────────────────────────────────────────
    scans: Mapped[list["Scan"]] = relationship(
        "Scan", back_populates="user", lazy="select"
    )

    def __repr__(self):
        return f"<User {self.email} | plan={self.plan}>"
