"""
A2 Sentinel — User Schemas
Pydantic models for request/response validation (User & Auth).
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


# ─── Request Schemas ────────────────────────────────────────────

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    full_name: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=1000)


# ─── Response Schemas ───────────────────────────────────────────

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    company: Optional[str]
    plan: str
    scans_used: int
    scans_limit: int
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUsageResponse(BaseModel):
    plan: str
    scans_used: int
    scans_limit: int
    scans_remaining: int
    simulations_used: int
    api_key: Optional[str]


# ─── Auth Response ──────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse
