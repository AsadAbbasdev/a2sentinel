"""
A2 Sentinel — User Routes
GET  /api/user/me          → profile
GET  /api/user/usage       → scan usage & limits
PUT  /api/user/profile     → update profile
POST /api/user/regenerate-key → new API key
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUsageResponse, UserUpdateRequest
from app.api.dependencies import get_current_user
from app.services.auth_service import auth_service

router = APIRouter(prefix="/user", tags=["👤 User"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user's profile and plan info."""
    return UserResponse.model_validate(current_user)


@router.get(
    "/usage",
    response_model=UserUsageResponse,
    summary="Get scan usage and API key",
)
async def get_usage(current_user: User = Depends(get_current_user)):
    """
    Returns:
    - Current plan
    - Scans used / remaining
    - Your API key for programmatic access
    """
    return UserUsageResponse(
        plan=current_user.plan,
        scans_used=current_user.scans_used,
        scans_limit=current_user.scans_limit,
        scans_remaining=max(0, current_user.scans_limit - current_user.scans_used),
        simulations_used=current_user.simulations_used,
        api_key=current_user.api_key,
    )


@router.put(
    "/profile",
    response_model=UserResponse,
    summary="Update profile",
)
async def update_profile(
    data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update full name, company, or bio."""
    if data.full_name is not None:
        current_user.full_name = data.full_name
    if data.company is not None:
        current_user.company = data.company
    if data.bio is not None:
        current_user.bio = data.bio
    await db.flush()
    return UserResponse.model_validate(current_user)


@router.post(
    "/regenerate-key",
    summary="Generate a new API key",
)
async def regenerate_api_key(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generates a fresh API key and invalidates the old one.
    Use this if your key is compromised.
    """
    new_key = await auth_service.regenerate_api_key(db, current_user)
    return {
        "message": "API key regenerated. Update your integrations.",
        "api_key": new_key,
    }
