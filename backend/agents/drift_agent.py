"""Compliance Drift Agent — monitors changes over time (STUB)."""
from backend.agents.base import BaseAgent
from backend.graph.parsers import load_all_findings


class DriftAgent(BaseAgent):
    name = "drift"
    description = "Monitors compliance drift between scans"
    is_real = False

    def run(self, context: dict) -> dict:
        findings = load_all_findings()
        return {
            "agent": self.name,
            "status": "baseline_only",
            "message": "Drift monitoring requires a historical baseline. This scan establishes the baseline.",
            "baseline_findings": len(findings),
            "next_scan": "Run again after code changes to detect drift.",
        }
