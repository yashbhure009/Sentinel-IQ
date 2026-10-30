"""Compliance Agent — policy Q&A (uses P1 RAG if available, else honest stub)."""
from backend.agents.base import BaseAgent

try:
    from backend.rag.pipeline import ask_policy
    _HAS_RAG = True
except (ImportError, AttributeError):
    _HAS_RAG = False


class ComplianceAgent(BaseAgent):
    name = "compliance"
    description = "Analyzes policies and answers compliance questions"
    is_real = _HAS_RAG

    def run(self, context: dict) -> dict:
        question = context.get("question", "Do we encrypt data at rest?")
        if _HAS_RAG:
            result = ask_policy(question)
            return {"agent": self.name, "question": question, **result}
        return {
            "agent": self.name,
            "question": question,
            "status": "rag_not_implemented",
            "message": "Policy Q&A requires the RAG pipeline. Coming soon — policy docs are loaded.",
            "policies_available": [
                "encryption_policy.md",
                "access_control_policy.md",
                "secrets_management_policy.md",
                "logging_policy.md",
            ],
        }
