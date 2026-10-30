"""Evidence Gathering Agent — surfaces scan artifacts as evidence (STUB)."""
from pathlib import Path
from backend.agents.base import BaseAgent

SCANS = Path(__file__).parent.parent / "graph" / "scans"


class EvidenceAgent(BaseAgent):
    name = "evidence"
    description = "Collects and presents evidence for findings"
    is_real = False

    def run(self, context: dict) -> dict:
        evidence = []
        for f in ["checkov_output.json", "pip_audit.json", "SUMMARY.md"]:
            p = SCANS / f
            if p.exists():
                evidence.append({
                    "file": f,
                    "size_bytes": p.stat().st_size,
                    "kind": "scan-output",
                })
        return {
            "agent": self.name,
            "evidence_sources": evidence,
            "message": "GitHub/AWS/Jira integrations are on the roadmap. Current evidence comes from scan artifacts.",
        }
