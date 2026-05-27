"""
A2 Sentinel — Helper Utilities Tests
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.utils.helpers import (
    detect_language_from_filename,
    calculate_security_grade,
    format_scan_duration,
    extract_code_language_hint,
)


class TestDetectLanguage:
    def test_python_file(self):
        assert detect_language_from_filename("main.py") == "python"

    def test_javascript_file(self):
        assert detect_language_from_filename("app.js") == "javascript"

    def test_typescript_file(self):
        assert detect_language_from_filename("index.ts") == "typescript"

    def test_php_file(self):
        assert detect_language_from_filename("index.php") == "php"

    def test_unknown_extension(self):
        assert detect_language_from_filename("file.xyz") is None

    def test_no_filename(self):
        assert detect_language_from_filename(None) is None


class TestSecurityGrade:
    def test_aplus(self):
        assert calculate_security_grade(98) == "A+"

    def test_a(self):
        assert calculate_security_grade(88) == "A"

    def test_b(self):
        assert calculate_security_grade(75) == "B"

    def test_c(self):
        assert calculate_security_grade(60) == "C"

    def test_d(self):
        assert calculate_security_grade(40) == "D"

    def test_f(self):
        assert calculate_security_grade(10) == "F"


class TestFormatDuration:
    def test_milliseconds(self):
        assert format_scan_duration(500) == "500ms"

    def test_seconds(self):
        assert format_scan_duration(2500) == "2.5s"

    def test_minutes(self):
        assert format_scan_duration(90000) == "1.5m"
