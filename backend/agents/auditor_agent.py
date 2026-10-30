"""Auditor Simulation Agent — plain-language control explanations (STUB with templates)."""
from backend.agents.base import BaseAgent

TEMPLATES = {
    "A.8.24": {
        "requires": "Encryption of data at rest and in transit using approved algorithms.",
        "why": "Prevents unauthorized disclosure of sensitive data if storage or transport is compromised.",
        "evidence": "S3/RDS encryption settings, TLS policy on load balancers.",
    },
    "A.8.3": {
        "requires": "Access to information and systems is restricted based on business need-to-know.",
        "why": "Limits blast radius of compromised credentials or accounts.",
        "evidence": "S3 bucket ACLs, IAM policies, security group rules.",
    },
    "A.8.20": {
        "requires": "Networks are secured and managed to protect information systems.",
        "why": "Prevents unauthorized access and lateral movement within the network.",
        "evidence": "Security group rules, network ACLs, firewall configuration.",
    },
}


class AuditorAgent(BaseAgent):
    name = "auditor"
    description = "Explains controls and simulates auditor questions"
    is_real = False

    def run(self, context: dict) -> dict:
        control_id = context.get("control_id", "A.8.24")
        template = TEMPLATES.get(control_id, {
            "requires": "Control requirements not yet loaded for {}.".format(control_id),
            "why": "Business rationale pending.",
            "evidence": "Evidence types pending.",
        })
        return {
            "agent": self.name,
            "control_id": control_id,
            **template,
        }
