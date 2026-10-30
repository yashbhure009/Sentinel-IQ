"""Risk Assessment Agent — prioritizes findings by severity (STUB, rule-based)."""
from backend.agents.base import BaseAgent
from backend.graph.parsers import load_all_findings

SEVERITY_WEIGHT = {"critical": 10, "high": 5, "medium": 2, "low": 1}


class RiskAgent(BaseAgent):
    name = "risk"
    description = "Prioritizes findings by business risk"
    is_real = False

    def run(self, context: dict) -> dict:
        findings = load_all_findings()
        scored = [(f, SEVERITY_WEIGHT.get(f.severity, 1)) for f in findings]
        scored.sort(key=lambda x: -x[1])
        top = scored[:10]
        return {
            "agent": self.name,
            "total_findings": len(findings),
            "scoring": "severity-weighted (rule-based)",
            "top_10": [
                {"id": f.id, "type": f.type, "severity": f.severity, "score": s, "description": f.description[:60]}
                for f, s in top
            ],
            "message": "Custom risk scoring with asset criticality is on the roadmap.",
        }
