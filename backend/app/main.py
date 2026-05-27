"""
A2 Sentinel — FastAPI Application
"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.database import create_tables
from app.api.routes import auth, scan, user

# ─── Setup logging ───────────────────────────────────────────────
setup_logging()

# ─── App Lifecycle ───────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    if not settings.is_production:
        await create_tables()
        logger.info("Database tables verified")
    yield
    logger.info(f"{settings.APP_NAME} shutting down")


# ─── FastAPI App ─────────────────────────────────────────────────
app = FastAPI(
    title="A2 Sentinel",
    description="""
## 🛡️ A2 Sentinel — AI-Powered Security Scanning

### Core APIs
| Endpoint | Description |
|---|---|
| `POST /api/scan` | Scan code for vulnerabilities |
| `POST /api/scan/simulate` | Attack simulation |
| `POST /api/scan/fix` | Auto-generate secure code |
| `GET /api/scan/history` | Scan history |

### Authentication
- **Bearer Token**: `Authorization: Bearer <jwt_token>`
- **API Key**: `X-API-Key: a2s_<your_key>`
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS ────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request Logger ──────────────────────────────────────────────
@app.middleware("http")
async def request_logger(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000, 1)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} [{duration_ms}ms]")
    response.headers["X-Response-Time"] = f"{duration_ms}ms"
    return response

# ─── Global Error Handler ────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Our team has been notified."},
    )

# ─── Routes ──────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api")
app.include_router(scan.router, prefix="/api")
app.include_router(user.router, prefix="/api")

# ─── System Endpoints ────────────────────────────────────────────
@app.get("/", tags=["System"], include_in_schema=False)
async def root():
    return {
        "product": "A2 Sentinel",
        "tagline": "AI-powered security scanning",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "A2 Sentinel",
        "version": settings.APP_VERSION,
    }