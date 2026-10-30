"""Security finding and graph API routes."""
from fastapi import APIRouter
from backend.schemas import Finding, Mapping
from backend.graph.parsers import load_all_findings
from backend.graph.mapper import map_finding

router = APIRouter()

_FINDINGS = load_all_findings()


@router.get("/findings", response_model=list[Finding])
def get_findings() -> list[Finding]:
    return _FINDINGS


@router.post("/map", response_model=list[Mapping])
def post_map(finding: Finding) -> list[Mapping]:
    return map_finding(finding)
