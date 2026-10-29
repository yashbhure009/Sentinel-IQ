"""Security finding and graph API routes."""
from fastapi import APIRouter
from backend.schemas import Finding, Mapping
from backend.graph.parsers import load_all_findings
from backend.graph.mapper import map_finding

router = APIRouter()

# Load once at startup — the scan files are static
_FINDINGS = load_all_findings()


@router.get("/findings", response_model=list[Finding])
def get_findings() -> list[Finding]:
    """Return all normalized findings from the latest scan."""
    return _FINDINGS


@router.post("/map", response_model=list[Mapping])
def post_map(finding: Finding) -> list[Mapping]:
    """Map a single finding to controls across all frameworks (deterministic)."""
    return map_finding(finding)
