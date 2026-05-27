import time
import uuid
from datetime import datetime
from typing import Optional
from loguru import logger

from app.services.ai_engine import ai_engine
from app.services.rule_scanner import rule_scanner
from app.schemas.scan import (
    ScanRequest,
    ScanResponse,
    ScanStatus,
    Vulnerability,
    VulnerabilitySummary,
    AttackSimulation,
    CodeFix,
    RiskLevel,
)

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


class ScanService:

    async def run_scan(self, request: ScanRequest, user_id: str) -> ScanResponse:
        scan_id = str(uuid.uuid4())
        start_ms = int(time.time() * 1000)
        logger.info(f"[{scan_id[:8]}] Scan started | user={user_id[:8]}")

        rule_findings = rule_scanner.scan(request.code, request.language)
        ai_result = await ai_engine.scan_code(request.code, request.language)
        vulnerabilities = self._merge_findings(ai_result, rule_findings)

        simulations = None
        if request.include_simulation and vulnerabilities:
            simulations = await self._run_simulations(request.code, request.language, vulnerabilities[:3])

        fix = None
        if request.include_fix:
            try:
                fix_data = await ai_engine.generate_fix(request.code, request.language)
                fix = CodeFix(**fix_data)
            except Exception as e:
                logger.error(f"Fix generation failed: {e}")

        duration_ms = int(time.time() * 1000) - start_ms
        counts = rule_scanner.get_severity_counts([v.model_dump() for v in vulnerabilities])

        vuln_summary = VulnerabilitySummary(
            total=len(vulnerabilities),
            critical=counts["critical"],
            high=counts["high"],
            medium=counts["medium"],
            low=counts["low"],
            info=counts["info"],
        )

        score = float(ai_result.get("security_score", 50))
        risk_raw = ai_result.get("risk_level", "medium").lower()
        risk_level = RiskLevel(risk_raw) if risk_raw in RiskLevel._value2member_map_ else RiskLevel.medium

        logger.info(f"[{scan_id[:8]}] Done | score={score} | vulns={len(vulnerabilities)} | {duration_ms}ms")

        return ScanResponse(
            scan_id=scan_id,
            status=ScanStatus.completed,
            security_score=score,
            risk_level=risk_level,
            summary=ai_result.get("summary", "Scan complete."),
            vulnerability_summary=vuln_summary,
            vulnerabilities=vulnerabilities,
            simulations=simulations,
            fix=fix,
            scan_duration_ms=duration_ms,
            created_at=datetime.utcnow(),
        )

    def _merge_findings(self, ai_result: dict, rule_findings: list) -> list[Vulnerability]:
        seen_titles = set()
        merged = []

        for v in ai_result.get("vulnerabilities", []):
            try:
                vuln = Vulnerability(**v)
                key = vuln.title.lower()[:40]
                if key not in seen_titles:
                    seen_titles.add(key)
                    merged.append(vuln)
            except Exception as e:
                logger.warning(f"Skipping AI finding: {e}")

        for finding in rule_findings:
            key = finding["title"].lower()[:40]
            if key not in seen_titles:
                seen_titles.add(key)
                try:
                    merged.append(Vulnerability(**finding))
                except Exception as e:
                    logger.warning(f"Skipping rule finding: {e}")

        merged.sort(key=lambda x: SEVERITY_ORDER.get(x.severity, 5))
        return merged

    async def _run_simulations(self, code, language, vulnerabilities):
        simulations = []
        for vuln in vulnerabilities:
            try:
                sim_data = await ai_engine.simulate_attack(code, language, vuln.title)
                sim_data["vulnerability_id"] = vuln.id
                if "attack_name" not in sim_data:
                    sim_data["attack_name"] = f"Attack on {vuln.title}"
                simulations.append(AttackSimulation(**sim_data))
            except Exception as e:
                logger.error(f"Simulation failed for {vuln.title}: {e}")
        return simulations


scan_service = ScanService()