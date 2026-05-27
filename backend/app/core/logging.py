"""
A2 Sentinel — Logging Configuration
Uses loguru for structured, colored logs.
"""

import sys
from loguru import logger
from app.core.config import settings


def setup_logging():
    """Configure loguru logger for A2 Sentinel."""
    logger.remove()  # Remove default handler

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Console output
    logger.add(
        sys.stdout,
        format=log_format,
        level="DEBUG" if settings.DEBUG else "INFO",
        colorize=True,
    )

    # File output (production)
    if settings.is_production:
        logger.add(
            "logs/a2sentinel_{time:YYYY-MM-DD}.log",
            format=log_format,
            level="INFO",
            rotation="1 day",
            retention="30 days",
            compression="gz",
        )

    return logger
