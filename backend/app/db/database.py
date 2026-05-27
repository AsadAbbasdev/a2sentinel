"""
A2 Sentinel — Database Setup
Async SQLAlchemy engine + session factory + base model class.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase


# ─── Async Engine ───────────────────────────────────────────────
engine = create_async_engine(
    "postgresql+asyncpg://postgres:pass123@localhost:5433/a2_sentinel",
    echo=True,      # logs all SQL in debug mode
    pool_pre_ping=True,        # verify connections before use
    pool_size=10,              # base pool size
    max_overflow=20,           # extra connections allowed
    pool_recycle=3600,         # recycle connections every hour
)

# ─── Session Factory ────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,    # keep objects usable after commit
)


# ─── Base Model Class ───────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# ─── Dependency ─────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    """
    FastAPI dependency — provides a database session per request.
    Auto commits on success, rolls back on exception.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all tables (used in development / testing)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Drop all tables (used in testing only)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
