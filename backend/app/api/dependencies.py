"""
A2 Sentinel — API Dependencies
FastAPI dependency injection for auth, quota checking, and DB sessions.
"""

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from loguru import logger

from app.db.database import get_db
from app.core.security import decode_token
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Authenticate request via JWT Bearer token OR X-API-Key header.

    JWT:     Used by the web dashboard (short-lived, 60 min)
    API Key: Used for programmatic access (long-lived, rotatable)
    """
    user = None

    # ── Try JWT Bearer ───────────────────────────────────────────
    if credentials:
        payload = decode_token(credentials.credentials)
        if payload:
            user_id = payload.get("sub")
            if user_id:
                result = await db.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()

    # ── Try API Key ──────────────────────────────────────────────
    if not user and x_api_key:
        result = await db.execute(select(User).where(User.api_key == x_api_key))
        user = result.scalar_one_or_none()

    # ── Reject if neither worked ─────────────────────────────────
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide a Bearer token or X-API-Key header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact support@a2sentinel.com",
        )

    return user


async def get_current_user_with_quota(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Same as get_current_user but also enforces scan quota.
    Use this for any endpoint that consumes a scan credit.
    """
    if current_user.scans_used >= current_user.scans_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Scan limit reached ({current_user.scans_used}/{current_user.scans_limit}). "
                f"Upgrade your plan at https://a2sentinel.com/pricing"
            ),
        )
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Only allows admin users."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user
