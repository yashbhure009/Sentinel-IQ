"""Crypto Assurance Agent — filters crypto-related findings (REAL)."""
from backend.agents.base import BaseAgent
from backend.graph.parsers import load_all_findings

CRYPTO_TYPES = {"unencrypted_storage", "weak_tls", "hardcoded_secret"}


class CryptoAssuranceAgent(BaseAgent):
    name = "crypto_assurance"
    description = "Evaluates TLS, secrets, and encryption-at-rest practices"
    is_real = True

    def run(self, context: dict) -> dict:
        findings = load_all_findings()
        crypto = [f for f in findings if f.type in CRYPTO_TYPES]
        by_type = {}
        for f in crypto:
            by_type[f.type] = by_type.get(f.type, 0) + 1
        return {
            "agent": self.name,
            "total_findings": len(crypto),
            "by_type": by_type,
            "findings": [f.model_dump() for f in crypto[:10]],
        }
