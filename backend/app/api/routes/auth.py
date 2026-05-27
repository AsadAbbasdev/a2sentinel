"""
A2 Sentinel — Auth Routes
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh  (future)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.user import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.services.auth_service import auth_service
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["🔐 Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
)
async def register(
    data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new A2 Sentinel account.

    - Returns JWT access token + user info
    - New accounts start on the **free plan** (10 scans)
    - An API key is generated automatically for programmatic access
    """
    try:
        user = await auth_service.register(db, data)
        token = auth_service.create_token(user)
        return TokenResponse(
            access_token=token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get access token",
)
async def login(
    data: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Login with email and password.

    Returns a JWT token valid for `ACCESS_TOKEN_EXPIRE_MINUTES`.
    Use this token in the `Authorization: Bearer <token>` header.
    """
    try:
        user = await auth_service.login(db, data.email, data.password)
        token = auth_service.create_token(user)
        return TokenResponse(
            access_token=token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
