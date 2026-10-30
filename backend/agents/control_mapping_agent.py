"""Control Mapping Agent — deterministic finding → controls (REAL)."""
from backend.agents.base import BaseAgent
from backend.graph.mapper import map_finding
from backend.schemas import Finding


class ControlMappingAgent(BaseAgent):
    name = "control_mapping"
    description = "Maps a finding to controls across ISO/NIST/SOC2/CIS/PCI"
    is_real = True

    def run(self, context: dict) -> dict:
        finding = Finding(**context["finding"])
        mappings = map_finding(finding)
        return {
            "agent": self.name,
            "finding_id": finding.id,
            "mappings": [m.model_dump() for m in mappings],
            "count": len(mappings),
        }
