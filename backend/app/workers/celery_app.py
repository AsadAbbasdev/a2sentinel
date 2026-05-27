"""
A2 Sentinel — Celery Task Queue
Handles heavy async jobs:
  - Large file / repo scans
  - Batch scanning
  - Report generation
  - Email notifications
"""

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "a2_sentinel",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,              # retry on worker crash
    worker_prefetch_multiplier=1,     # one task at a time per worker
    task_soft_time_limit=300,         # 5 min soft limit
    task_time_limit=600,              # 10 min hard limit
)
