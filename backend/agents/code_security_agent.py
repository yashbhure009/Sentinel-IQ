"""Code Security Agent — exposes scan findings (REAL)."""
from backend.agents.base import BaseAgent
from backend.graph.parsers import load_all_findings


class CodeSecurityAgent(BaseAgent):
    name = "code_security"
    description = "Static security analysis of Terraform, Dockerfile, and code"
    is_real = True

    def run(self, context: dict) -> dict:
        findings = load_all_findings()
        # Only config findings (not dependency CVEs)
        config = [f for f in findings if f.type != "vulnerable_dependency"]
        by_type = {}
        for f in config:
            by_type[f.type] = by_type.get(f.type, 0) + 1
        return {
            "agent": self.name,
            "total_findings": len(config),
            "by_type": by_type,
            "sample": [f.model_dump() for f in config[:5]],
        }
