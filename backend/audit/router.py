"""Security audit API routes."""
from fastapi import APIRouter
from pydantic import BaseModel
from backend.schemas import AuditReport
from backend.audit.engine import run_audit

router = APIRouter()


class AuditRequest(BaseModel):
    framework: str = "ISO 27001"


@router.post("/audit", response_model=AuditReport)
def post_audit(req: AuditRequest) -> AuditReport:
    return run_audit(req.framework)
