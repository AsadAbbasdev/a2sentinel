"""
A2 Sentinel — AI Engine
Groq (FREE) use kar raha hai — llama-3.3-70b model
Jab production mein jao to PROVIDER=anthropic kar do .env mein
"""

import json
import re
from typing import Optional
from openai import OpenAI  # Groq OpenAI-compatible hai
from app.core.config import settings
from loguru import logger


# ════════════════════════════════════════════════════════════════
#  SYSTEM PROMPTS — same rahenge provider change ho ya na ho
# ════════════════════════════════════════════════════════════════

SCAN_SYSTEM_PROMPT = """You are A2 Sentinel's AI Security Engine — an elite cybersecurity AI that thinks like both an attacker AND a defender.

Your mission: Analyze code deeply and find ALL security vulnerabilities. Think like a hacker trying to break this code.

Rules:
- Be thorough. Don't miss anything, even subtle issues.
- Be specific. Name the exact line, variable, or function that is vulnerable.
- Be realistic. Describe how a real attacker would exploit this, not just theory.
- Be actionable. Every vulnerability must have a concrete fix.
- Score the code 0-100 (100 = perfectly secure, 0 = critically broken).

IMPORTANT: Respond with valid JSON ONLY. No markdown, no explanation outside JSON.

Response format:
{
  "security_score": <integer 0-100>,
  "risk_level": "<critical|high|medium|low>",
  "summary": "<2-3 sentence executive summary>",
  "vulnerabilities": [
    {
      "id": "ai_001",
      "title": "<short descriptive title>",
      "severity": "<critical|high|medium|low|info>",
      "description": "<what is wrong, why it matters, attacker perspective>",
      "line_number": <integer or null>,
      "code_snippet": "<the exact vulnerable code>",
      "owasp_category": "<e.g. A03:2021 - Injection>",
      "cwe_id": "<e.g. CWE-89>",
      "recommendation": "<specific, actionable fix with code example>",
      "references": ["<url1>"]
    }
  ]
}"""


SIMULATION_SYSTEM_PROMPT = """You are A2 Sentinel's Red Team AI — an ethical hacker running attack simulations for defensive education.

Given vulnerable code, simulate a REAL attack scenario with exact payloads.

Respond with valid JSON ONLY:
{
  "attack_name": "<name of attack technique>",
  "attacker_profile": "<script kiddie | APT | insider>",
  "attack_steps": [
    {
      "step": 1,
      "action": "<what attacker does>",
      "payload": "<exact payload or command>",
      "expected_result": "<what happens>"
    }
  ],
  "impact": "<business impact — data at risk, potential damage>",
  "proof_of_concept": "<working exploit code or command>",
  "cvss_score": <0.0-10.0>,
  "time_to_exploit": "<minutes|hours|days>",
  "prerequisites": "<what attacker needs>"
}"""


FIX_SYSTEM_PROMPT = """You are A2 Sentinel's Secure Code AI — a senior security engineer who writes bulletproof code.

Your mission: Take vulnerable code and return a fully secured, production-ready version.

CRITICAL JSON RULES:
- Return ONLY valid JSON
- In "fixed_code" field, use \\n for newlines, NOT actual newlines
- Escape all backslashes as \\\\
- Escape all quotes inside strings as \\"
- No control characters inside JSON strings

Respond with valid JSON ONLY:
{
  "fixed_code": "def get_user(user_id: int):\\n    cursor.execute(\\"SELECT * FROM users WHERE id = %s\\", (user_id,))\\n    return cursor.fetchone()",
  "changes_made": ["<change 1>", "<change 2>"],
  "explanation": "<what was vulnerable and how fixed>",
  "additional_recommendations": ["<tip 1>"],
  "security_libraries_used": ["<lib1>"]
}"""


# ════════════════════════════════════════════════════════════════
#  AI ENGINE — supports Groq (free) and Anthropic (paid)
# ════════════════════════════════════════════════════════════════

class AIEngine:

    def __init__(self):
        self.provider = settings.AI_PROVIDER  # "groq" ya "anthropic"
        self._setup_client()

    def _setup_client(self):
        """Provider ke hisaab se client setup karo."""
        if self.provider == "groq":
            self.client = OpenAI(
                api_key=settings.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
            )
            self.model = settings.GROQ_MODEL
            logger.info(f"AI Engine: Groq | model={self.model}")

        elif self.provider == "anthropic":
            # Anthropic bhi OpenAI-compatible wrapper se use kar sakte hain
            # ya native client — yahan openai wrapper use kar rahe hain simplicity ke liye
            import anthropic as ant
            self._anthropic_client = ant.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = settings.AI_MODEL
            logger.info(f"AI Engine: Anthropic | model={self.model}")

        else:
            raise ValueError(f"Unknown AI_PROVIDER: {self.provider}. Use 'groq' or 'anthropic'")

    def _call_ai(self, system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
        """
        Unified AI call — works with both Groq and Anthropic.
        """
        try:
            if self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=0.1,  # low temperature = consistent JSON output
                )
                return response.choices[0].message.content

            elif self.provider == "anthropic":
                response = self._anthropic_client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}],
                )
                return response.content[0].text

        except Exception as e:
            logger.error(f"AI call failed [{self.provider}]: {e}")
            raise ValueError(f"AI engine error: {str(e)}")

    def _parse_json(self, raw: str) -> dict:
        # Remove markdown fences
        cleaned = re.sub(r"```(?:json)?\n?", "", raw).strip().rstrip("`").strip()
        
        # Fix invalid escape sequences
        cleaned = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', cleaned)
        
        # Fix control characters
        cleaned = re.sub(r'[\x00-\x1f\x7f](?<![\n\r\t])', '', cleaned)
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Extract JSON object
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                try:
                    extracted = match.group()
                    extracted = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', extracted)
                    return json.loads(extracted)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error: {e} | Raw: {raw[:300]}")
                    raise ValueError(f"AI returned malformed JSON: {e}")
            raise ValueError("No valid JSON found in AI response")

    def _build_message(self, code: str, language: Optional[str], extra: str = "") -> str:
        lang = f"Language: {language}\n" if language else ""
        return f"{lang}{extra}\n\nCode:\n```\n{code}\n```"

    # ─── Public Methods ─────────────────────────────────────────

    async def scan_code(self, code: str, language: Optional[str] = None) -> dict:
        """Vulnerability scan — returns score, risk_level, vulnerabilities list."""
        logger.info(f"AI scan | provider={self.provider} | lang={language} | chars={len(code)}")
        msg = self._build_message(code, language, "Analyze this code for ALL security vulnerabilities.")
        raw = self._call_ai(SCAN_SYSTEM_PROMPT, msg)
        result = self._parse_json(raw)
        logger.info(f"Scan done | score={result.get('security_score')} | vulns={len(result.get('vulnerabilities', []))}")
        return result

    async def simulate_attack(self, code: str, language: Optional[str] = None, target_vulnerability: Optional[str] = None) -> dict:
        """Attack simulation — step by step exploit with payloads."""
        logger.info(f"Attack simulation | target={target_vulnerability}")
        focus = f"Focus on: {target_vulnerability}" if target_vulnerability else ""
        msg = self._build_message(code, language, f"Simulate a real attack. {focus}")
        raw = self._call_ai(SIMULATION_SYSTEM_PROMPT, msg, max_tokens=2048)
        return self._parse_json(raw)

    async def generate_fix(self, code: str, language: Optional[str] = None, context: Optional[str] = None) -> dict:
        """Secure fix generation — returns patched code + explanation."""
        logger.info("Generating secure fix")
        extra = f"Context: {context}" if context else "Fix all security vulnerabilities."
        msg = self._build_message(code, language, extra)
        raw = self._call_ai(FIX_SYSTEM_PROMPT, msg)
        return self._parse_json(raw)


# Singleton
ai_engine = AIEngine()
