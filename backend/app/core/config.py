"""
A2 Sentinel — Configuration
.env file se saari settings load hoti hain.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # ─── App ────────────────────────────────────────────────────
    APP_NAME: str = "A2 Sentinel"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # ─── Security ───────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ─── Database ───────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/a2_sentinel"
    DATABASE_URL_SYNC: str = "postgresql://postgres:password@localhost:5432/a2_sentinel"

    # ─── Redis ──────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ─── AI Provider ────────────────────────────────────────────
    # "groq" = free  |  "anthropic" = paid (production)
    AI_PROVIDER: str = "groq"

    # Groq (FREE) — groq.com se free API key lo
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Anthropic (PAID) — baad mein production mein use karo
    ANTHROPIC_API_KEY: str = ""
    AI_MODEL: str = "claude-opus-4-5"
    AI_MAX_TOKENS: int = 4096

    # ─── Rate Limiting ──────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 30
    RATE_LIMIT_PER_HOUR: int = 200

    # ─── Plan Scan Limits ───────────────────────────────────────
    FREE_PLAN_SCAN_LIMIT: int = 10
    PRO_PLAN_SCAN_LIMIT: int = 500
    TEAM_PLAN_SCAN_LIMIT: int = 2000
    ENTERPRISE_PLAN_SCAN_LIMIT: int = 999999

    # ─── CORS ───────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    def get_scan_limit(self, plan: str) -> int:
        return {
            "free": self.FREE_PLAN_SCAN_LIMIT,
            "pro": self.PRO_PLAN_SCAN_LIMIT,
            "team": self.TEAM_PLAN_SCAN_LIMIT,
            "enterprise": self.ENTERPRISE_PLAN_SCAN_LIMIT,
        }.get(plan, self.FREE_PLAN_SCAN_LIMIT)

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
