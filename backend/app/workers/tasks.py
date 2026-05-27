"""
A2 Sentinel — Background Tasks
Celery tasks for async processing of heavy operations.
"""

import asyncio
from loguru import logger
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="tasks.async_scan")
def async_scan_task(self, scan_id: str, code: str, language: str, user_id: str):
    """
    Background scan task for large codebases.
    Called when code > 10,000 chars or repo scanning.
    """
    logger.info(f"Background scan started | task_id={self.request.id} | scan_id={scan_id}")
    try:
        # Import here to avoid circular imports
        from app.services.scan_service import scan_service
        from app.schemas.scan import ScanRequest

        request = ScanRequest(code=code, language=language)
        result = asyncio.run(scan_service.run_scan(request, user_id))

        logger.info(f"Background scan complete | scan_id={scan_id} | score={result.security_score}")
        return {
            "scan_id": scan_id,
            "status": "completed",
            "security_score": result.security_score,
            "total_vulnerabilities": result.vulnerability_summary.total,
        }
    except Exception as e:
        logger.error(f"Background scan failed | scan_id={scan_id} | error={e}")
        self.retry(exc=e, countdown=30, max_retries=2)


@celery_app.task(name="tasks.send_scan_alert")
def send_scan_alert_task(user_email: str, scan_id: str, critical_count: int):
    """
    Send email/Slack alert when critical vulnerabilities found.
    (Email integration to be added in Phase 2)
    """
    logger.info(
        f"Alert queued | email={user_email} | scan={scan_id} | critical={critical_count}"
    )
    # TODO Phase 2: integrate SMTP / Slack webhook
    return {"status": "queued", "recipient": user_email}
