"""Shared Pydantic schemas for SentinelIQ API contracts."""

from pydantic import BaseModel


class Finding(BaseModel):
    """Placeholder schema for a security finding."""

    id: str
    title: str
    severity: str


class Mapping(BaseModel):
    """Placeholder schema for a finding-to-control mapping."""

    finding_id: str
    control_id: str


class Citation(BaseModel):
    """Placeholder schema for a policy citation."""

    source: str
    quote: str = ""


class PolicyAnswer(BaseModel):
    """Placeholder schema for a policy answer."""

    answer: str
    citations: list[Citation] = []


class AuditItem(BaseModel):
    """Placeholder schema for one audit item."""

    control_id: str
    status: str


class AuditReport(BaseModel):
    """Placeholder schema for an audit report."""

    items: list[AuditItem] = []
