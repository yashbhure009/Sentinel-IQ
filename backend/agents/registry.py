"""Central registry of all SentinelIQ agents."""
from backend.agents.compliance_agent import ComplianceAgent
from backend.agents.control_mapping_agent import ControlMappingAgent
from backend.agents.code_security_agent import CodeSecurityAgent
from backend.agents.crypto_assurance_agent import CryptoAssuranceAgent
from backend.agents.drift_agent import DriftAgent
from backend.agents.auditor_agent import AuditorAgent
from backend.agents.evidence_agent import EvidenceAgent
from backend.agents.risk_agent import RiskAgent

AGENTS = {
    "compliance": ComplianceAgent(),
    "control_mapping": ControlMappingAgent(),
    "code_security": CodeSecurityAgent(),
    "crypto_assurance": CryptoAssuranceAgent(),
    "drift": DriftAgent(),
    "auditor": AuditorAgent(),
    "evidence": EvidenceAgent(),
    "risk": RiskAgent(),
}


def get_agent(name: str):
    return AGENTS.get(name)
