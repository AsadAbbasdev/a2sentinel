"""
A2 Sentinel — Custom Exceptions
Centralized exception definitions for clean error handling.
"""

from fastapi import HTTPException, status


class A2SentinelException(Exception):
    """Base exception for A2 Sentinel."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


# ─── Auth Exceptions ────────────────────────────────────────────

class InvalidCredentialsError(A2SentinelException):
    pass


class EmailAlreadyExistsError(A2SentinelException):
    pass


class AccountDeactivatedError(A2SentinelException):
    pass


# ─── Scan Exceptions ────────────────────────────────────────────

class ScanLimitExceededError(A2SentinelException):
    pass


class ScanNotFoundError(A2SentinelException):
    pass


class AIEngineError(A2SentinelException):
    pass


class InvalidCodeError(A2SentinelException):
    pass


# ─── HTTP Exception Helpers ─────────────────────────────────────

def raise_401(detail: str = "Authentication required"):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def raise_403(detail: str = "Access forbidden"):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def raise_404(detail: str = "Resource not found"):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def raise_429(detail: str = "Rate limit exceeded"):
    raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


def raise_500(detail: str = "Internal server error"):
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
    )
