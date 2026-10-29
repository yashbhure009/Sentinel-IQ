"""SentinelIQ shared schemas — the data contract between all modules."""
from pydantic import BaseModel
from typing import Literal, Optional

FindingType = Literal[
    "hardcoded_secret",
    "vulnerable_dependency",
    "public_s3_bucket",
    "open_security_group",
    "weak_tls",
    "unencrypted_storage",
    "overly_permissive_iam",
    "missing_logging",
    "open_port",
]

Severity = Literal["low", "medium", "high", "critical"]


class Finding(BaseModel):
    id: str
    type: FindingType
    file: str
    line: Optional[int] = None
    severity: Severity
    source: str = "checkov"
    description: str


class Mapping(BaseModel):
    framework: str
    control_id: str
    title: str


class Citation(BaseModel):
    doc: str
    section: str
    snippet: str


class PolicyAnswer(BaseModel):
    answer: str
    citations: list[Citation]


class AuditItem(BaseModel):
    framework: str
    control_id: str
    title: str
    status: Literal["compliant", "gap", "missing_policy"]
    policy_citation: Optional[Citation] = None
    evidence: list[Finding] = []
    remediation: Optional[str] = None


class AuditReport(BaseModel):
    framework: str
    score: str
    items: list[AuditItem]
