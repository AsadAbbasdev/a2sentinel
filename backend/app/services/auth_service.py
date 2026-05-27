"""
A2 Sentinel â€” Auth Service
User registration, login, API key management.
"""

import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.models.user import User
from app.schemas.user import UserRegisterRequest
from app.core.security import verify_password, get_password_hash, create_access_token, create_api_key
from app.core.config import settings


class AuthService:

    async def register(self, db: AsyncSession, data: UserRegisterRequest) -> User:
        """
        Create a new user account.
        Raises ValueError if email already taken.
        """
        # Check duplicate email
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise ValueError(f"An account with email '{data.email}' already exists.")

        # Determine scan limit based on default free plan
        scan_limit = settings.get_scan_limit("free")

        user = User(
            id=str(uuid.uuid4()),
            email=data.email,
            full_name=data.full_name,
            company=data.company,
            hashed_password=get_password_hash(data.password[:72]),
            api_key=create_api_key(),
            plan="free",
            scans_limit=scan_limit,
        )
        db.add(user)
        await db.flush()
        logger.info(f"New user registered: {user.email}")
        return user

    async def login(self, db: AsyncSession, email: str, password: str) -> User:
        """
        Authenticate user with email + password.
        Raises ValueError on invalid credentials.
        """
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password.")

        if not user.is_active:
            raise ValueError("This account has been deactivated. Contact support.")

        # Update last login
        user.last_login_at = datetime.utcnow()
        await db.flush()

        logger.info(f"User logged in: {user.email}")
        return user

    async def get_by_id(self, db: AsyncSession, user_id: str) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_api_key(self, db: AsyncSession, api_key: str) -> User | None:
        result = await db.execute(select(User).where(User.api_key == api_key))
        return result.scalar_one_or_none()

    async def regenerate_api_key(self, db: AsyncSession, user: User) -> str:
        """Generate a new API key for the user."""
        user.api_key = create_api_key()
        await db.flush()
        logger.info(f"API key regenerated for: {user.email}")
        return user.api_key

    def create_token(self, user: User) -> str:
        """Create JWT access token for user."""
        return create_access_token({"sub": user.id, "email": user.email, "plan": user.plan})


auth_service = AuthService()

