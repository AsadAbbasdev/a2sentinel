"""
Rule-based Scanner — fast, deterministic detection of common vulnerabilities.
Covers OWASP Top 10 patterns before AI deep analysis.
This is Phase 1. Later: integrate Semgrep/Bandit for more rules.
"""

import re
from typing import Optional
import uuid


RULES = [
    # ─── SQL Injection ───────────────────────────────────────────
    {
        "id": lambda: f"rule_{uuid.uuid4().hex[:8]}",
        "title": "SQL Injection — string concatenation in query",
        "severity": "critical",
        "owasp_category": "A03:2021 - Injection",
        "cwe_id": "CWE-89",
        "pattern": re.compile(
            r'["\'].*(SELECT|INSERT|UPDATE|DELETE|WHERE).*["\']\s*\+',
            re.IGNORECASE,
        ),
        "recommendation": (
            "Use parameterized queries. Never concatenate user input into SQL. "
            "Example: cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
        ),
    },
    {
        "id": lambda: f"rule_{uuid.uuid4().hex[:8]}",
        "title": "SQL Injection — f-string in query",
        "severity": "critical",
        "owasp_category": "A03:2021 - Injection",
        "cwe_id": "CWE-89",
        "pattern": re.compile(
            r'f["\'].*(SELECT|INSERT|UPDATE|DELETE|WHERE)',
            re.IGNORECASE,
        ),
        "recommendation": "Replace f-string queries with parameterized queries.",
    },
    {
        "id": lambda: f"rule_{uuid.uuid4().hex[:8]}",
        "title": "SQL Injection — execute with string formatting",
        "severity": "critical",
        "owasp_category": "A03:2021 - Injection",
        "cwe_id": "CWE-89",
        "pattern": re.compile(
            r'(execute|query)\s*\(.*?(%\s*\(|\.format\(|%\s+[^,\)])',
            re.IGNORECASE,
        ),
        "recommendation": "Use parameterized queries with %s placeholders, not string formatting.",
    },
    # ─── XSS ─────────────────────────────────────────────────────
    {
        "id": lambda: f"rule_{uuid.uuid4().hex[:8]}",
        "title": "XSS — unescaped user input rendered to HTML",
        "severity": "high",
        "owasp_category": "A03:2021 - Injection (XSS)",
        "cwe_id": "CWE-79",
        "pattern": re.compile(
            r"innerHTML\s*=\s*.*?(req\.|request\.|params|query|body)",
            re.IGNORECASE,
        ),
        "recommendation": "Sanitize and escape all user input before rendering. Use textContent instead of innerHTML.",
    },
    # ─── Hardcoded Secrets ────────────────────────────────────────
    {
        "id": lambda: f"rule_{uuid.uuid4().hex[:8]}",
        "title": "Hardcoded Secret — password/key in source code",
        "severity": "high",
        "owasp_category": "A02:2021 - Cryptographic Failures",
        "cwe_id": "CWE-798",
        "pattern": re.compile(
            r'(password|secret|api_key|apikey|token)\s*=\s*["\'][^"\']{4,}["\']',
            re.IGNORECASE,
        ),
        "recommendation": "Move secrets to environment variables. Use a secrets manager in production.",
    },
    # ─── Command Injection ────────────────────────────────────────
    {
        "id": lambda: f"rule_{uuid.uuid4().hex[:8]}",
        "title": "Command Injection — user input in os.system / subprocess",
        "severity": "critical",
        "owasp_category": "A03:2021 - Injection",
        "cwe_id": "CWE-78",
        "pattern": re.compile(
            r"(os\.system|subprocess\.call|subprocess\.run|popen)\s*\(.*?(request|input|user|param)",
            re.IGNORECASE,
        ),
        "recommendation": (
            "Never pass user input directly to shell commands. "
            "Use subprocess with a list of arguments and shell=False."
        ),
    },
    # ─── Insecure Deserialization ─────────────────────────────────
    {
        "id": lambda: f"rule_{uuid.uuid4().hex[:8]}",
        "title": "Insecure Deserialization — pickle with user data",
        "severity": "critical",
        "owasp_category": "A08:2021 - Software and Data Integrity Failures",
        "cwe_id": "CWE-502",
        "pattern": re.compile(r"pickle\.loads?\s*\(.*?(request|user|input)", re.IGNORECASE),
        "recommendation": "Never deserialize untrusted data with pickle. Use JSON or authenticated serialization.",
    },
    # ─── Weak Crypto ──────────────────────────────────────────────
    {
        "id": lambda: f"rule_{uuid.uuid4().hex[:8]}",
        "title": "Weak Hashing — MD5 or SHA1 for passwords",
        "severity": "high",
        "owasp_category": "A02:2021 - Cryptographic Failures",
        "cwe_id": "CWE-327",
        "pattern": re.compile(r"(md5|sha1)\s*\(|hashlib\.(md5|sha1)", re.IGNORECASE),
        "recommendation": "Use bcrypt, Argon2, or PBKDF2 for password hashing. MD5/SHA1 are broken for security.",
    },
    # ─── Debug Mode ───────────────────────────────────────────────
    {
        "id": lambda: f"rule_{uuid.uuid4().hex[:8]}",
        "title": "Debug Mode Enabled in Production Code",
        "severity": "medium",
        "owasp_category": "A05:2021 - Security Misconfiguration",
        "cwe_id": "CWE-94",
        "pattern": re.compile(r"debug\s*=\s*True", re.IGNORECASE),
        "recommendation": "Set DEBUG=False in production. Use environment variables to control this.",
    },
]


class RuleScanner:
    def scan(self, code: str, language: Optional[str] = None) -> list:
        """Run all rules against code, return list of findings."""
        findings = []
        lines = code.splitlines()

        for rule in RULES:
            for line_num, line in enumerate(lines, start=1):
                if rule["pattern"].search(line):
                    findings.append({
                        "id": rule["id"](),
                        "title": rule["title"],
                        "severity": rule["severity"],
                        "description": (
                            f"Detected pattern matching {rule['title']}. "
                            "This requires immediate attention."
                        ),
                        "line_number": line_num,
                        "code_snippet": line.strip(),
                        "owasp_category": rule["owasp_category"],
                        "cwe_id": rule["cwe_id"],
                        "recommendation": rule["recommendation"],
                        "references": [
                            f"https://owasp.org/Top10/",
                            f"https://cwe.mitre.org/data/definitions/{rule['cwe_id'].split('-')[1]}.html",
                        ],
                    })
                    break  # one finding per rule per scan

        return findings
    
    def get_severity_counts(self, findings: list) -> dict:
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for f in findings:
            severity = f.get("severity", "info")
            if severity in counts:
                counts[severity] += 1
        return counts

rule_scanner = RuleScanner()
