"""
A2 Sentinel — Helper Utilities
Shared utility functions used across the application.
"""

import re
from typing import Optional


LANGUAGE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".php": "php",
    ".java": "java",
    ".rb": "ruby",
    ".go": "go",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".c": "c",
    ".rs": "rust",
    ".swift": "swift",
    ".kt": "kotlin",
    ".sql": "sql",
    ".sh": "bash",
}


def detect_language_from_filename(filename: Optional[str]) -> Optional[str]:
    """Detect programming language from file extension."""
    if not filename:
        return None
    ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
    return LANGUAGE_EXTENSIONS.get(ext)


def calculate_security_grade(score: float) -> str:
    """
    Convert numeric score to letter grade.
    A+ = 95-100, A = 85-94, B = 70-84, C = 50-69, D = 30-49, F = 0-29
    """
    if score >= 95:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 30:
        return "D"
    else:
        return "F"


def sanitize_code_for_log(code: str, max_chars: int = 100) -> str:
    """Truncate code for safe logging — avoid logging sensitive content."""
    return code[:max_chars].replace("\n", " ") + ("..." if len(code) > max_chars else "")


def extract_code_language_hint(code: str) -> Optional[str]:
    """
    Try to detect language from code content (shebang, imports, etc.)
    Used as fallback when language not explicitly provided.
    """
    first_lines = "\n".join(code.strip().splitlines()[:5]).lower()

    if "import " in first_lines and ("def " in code or "class " in code):
        return "python"
    if "const " in first_lines or "let " in first_lines or "function " in first_lines:
        return "javascript"
    if "<?php" in first_lines:
        return "php"
    if "public class " in first_lines or "import java." in first_lines:
        return "java"
    if "package main" in first_lines or "func main()" in code:
        return "go"
    return None


def format_scan_duration(ms: int) -> str:
    """Format milliseconds into human-readable string."""
    if ms < 1000:
        return f"{ms}ms"
    elif ms < 60000:
        return f"{ms / 1000:.1f}s"
    else:
        return f"{ms / 60000:.1f}m"
