"""
A2 Sentinel — Scan Routes
POST /api/scan           → full vulnerability scan
POST /api/scan/simulate  → attack simulation
POST /api/scan/fix       → auto-fix generation
GET  /api/scan/history   → scan history
GET  /api/scan/{scan_id} → get single scan result
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from loguru import logger

from app.db.database import get_db
from app.models.user import User
from app.models.scan import Scan
from app.schemas.scan import (
    ScanRequest,
    ScanResponse,
    SimulateRequest,
    FixRequest,
    ScanHistoryResponse,
    ScanHistoryItem,
)
from app.services.scan_service import scan_service
from app.services.ai_engine import ai_engine
from app.api.dependencies import get_current_user_with_quota, get_current_user

router = APIRouter(prefix="/scan", tags=["🔍 Security Scanning"])

from fastapi import Request as FastAPIRequest
from slowapi import Limiter
from slowapi.util import get_remote_address

# ─── Guest Scan (No Auth Required) ──────────────────────────────
@router.post(
    "/guest",
    summary="Free demo scan — no login required",
)
async def guest_scan(
    request: ScanRequest,
    http_request: FastAPIRequest,
):
    """
    ## Free Demo Scan — No Authentication Required
    
    - 1 free scan to try A2 Sentinel
    - Basic vulnerability detection only
    - No simulation or fix included
    - Sign up for full access
    """
    # Code length limit for guests
    if len(request.code) > 3000:
        raise HTTPException(
            status_code=400,
            detail="Guest scan limited to 3000 characters. Sign up for unlimited scanning."
        )

    try:
        # Force disable simulation and fix for guests
        guest_request = ScanRequest(
            code=request.code,
            language=request.language,
            filename=request.filename,
            include_simulation=False,
            include_fix=False,
        )

        result = await scan_service.run_scan(guest_request, user_id="guest")

        # Return limited result for guests
        return {
            "scan_id": result.scan_id,
            "status": result.status,
            "security_score": result.security_score,
            "risk_level": result.risk_level,
            "summary": result.summary,
            "vulnerability_summary": result.vulnerability_summary,
            "vulnerabilities": result.vulnerabilities[:5],  # max 5 vulns for guest
            "scan_duration_ms": result.scan_duration_ms,
            "created_at": result.created_at,
            "guest": True,
            "message": "Sign up free to see all vulnerabilities, attack simulation, and auto-fix!",
        }

    except Exception as e:
        logger.error(f"Guest scan error: {e}")
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

@router.post(
    "",
    response_model=ScanResponse,
    summary="Scan code for vulnerabilities",
)
async def scan_code(
    request: ScanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_quota),
):
    """
    ## A2 Sentinel Core Scan

    Analyzes your code using a **two-layer approach**:
    1. **Rule Scanner** — instant OWASP Top 10 pattern detection
    2. **AI Engine** — deep analysis, root cause, attacker perspective

    ### Optional extras:
    - `include_simulation: true` → attack simulation with real payloads
    - `include_fix: true` → generates a secure patched version

    ### Auth:
    `Authorization: Bearer <token>` or `X-API-Key: <your-key>`
    """
    try:
        result = await scan_service.run_scan(request, current_user.id)

        # Persist to database
        scan_record = Scan(
            user_id=current_user.id,
            code_snippet=request.code[:5000],
            language=request.language,
            filename=request.filename,
            status="completed",
            scan_type="code_scan",
            vulnerabilities=[v.model_dump() for v in result.vulnerabilities],
            simulations=[s.model_dump() for s in result.simulations] if result.simulations else None,
            suggested_fix=result.fix.model_dump() if result.fix else None,
            security_score=result.security_score,
            risk_level=result.risk_level,
            summary=result.summary,
            total_vulnerabilities=result.vulnerability_summary.total,
            critical_count=result.vulnerability_summary.critical,
            high_count=result.vulnerability_summary.high,
            medium_count=result.vulnerability_summary.medium,
            low_count=result.vulnerability_summary.low,
            scan_duration_ms=result.scan_duration_ms,
            completed_at=datetime.utcnow(),
        )
        db.add(scan_record)

        # Increment usage
        current_user.scans_used += 1
        await db.flush()

        return result

    except Exception as e:
        logger.error(f"Scan error for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.post(
    "/simulate",
    summary="Simulate a real attack on vulnerable code",
)
async def simulate_attack(
    request: SimulateRequest,
    current_user: User = Depends(get_current_user_with_quota),
):
    """
    ## Attack Simulation

    Shows you **exactly** how a hacker would exploit your code:
    - Step-by-step attack walkthrough
    - Real payloads (SQL injection strings, XSS vectors, etc.)
    - CVSS score and business impact

    Use `target_vulnerability` to focus on a specific vuln type.
    """
    try:
        result = await ai_engine.simulate_attack(
            request.code, request.language, request.target_vulnerability
        )
        return {"status": "success", "simulation": result}
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.post(
    "/fix",
    summary="Generate secure fixed version of code",
)
async def generate_fix(
    request: FixRequest,
    current_user: User = Depends(get_current_user_with_quota),
):
    """
    ## Auto Security Fix

    Generates a production-ready, secure version of your code:
    - All vulnerabilities patched
    - Inline comments explaining each fix
    - Additional security recommendations
    - Language best practices applied
    """
    try:
        result = await ai_engine.generate_fix(
            request.code, request.language, request.context
        )
        return {"status": "success", "fix": result}
    except Exception as e:
        logger.error(f"Fix generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Fix generation failed: {str(e)}")


@router.get(
    "/history",
    response_model=ScanHistoryResponse,
    summary="Get your scan history",
)
async def get_scan_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """
    Returns paginated scan history for the authenticated user.
    Most recent scans first.
    """
    offset = (page - 1) * per_page
    result = await db.execute(
        select(Scan)
        .where(Scan.user_id == current_user.id)
        .order_by(desc(Scan.created_at))
        .offset(offset)
        .limit(per_page)
    )
    scans = result.scalars().all()

    return ScanHistoryResponse(
        total=len(scans),
        page=page,
        per_page=per_page,
        scans=[ScanHistoryItem.model_validate(s) for s in scans],
    )


@router.get(
    "/{scan_id}",
    summary="Get a specific scan result",
)
async def get_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get full details of a specific scan by its ID."""
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id, Scan.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return scan
