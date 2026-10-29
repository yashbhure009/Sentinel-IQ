"""Framework-based security audit engine."""
import json
from pathlib import Path
from typing import Optional
from backend.schemas import AuditReport, AuditItem, Citation
from backend.graph.parsers import load_all_findings

_FRAMEWORKS = json.loads((Path(__file__).parent / "frameworks.json").read_text())

try:
    from backend.rag.coverage import policy_covers
except (ImportError, AttributeError):
    def policy_covers(control_id: str) -> Optional[Citation]:
        return None


def run_audit(framework: str) -> AuditReport:
    controls = _FRAMEWORKS.get(framework, [])
    findings = load_all_findings()
    items = []
    compliant = 0

    for ctrl in controls:
        evidence = [f for f in findings if f.type in ctrl["finding_types"]]
        citation = policy_covers(ctrl["control_id"])

        if citation is None:
            status = "missing_policy"
        elif evidence:
            status = "gap"
        else:
            status = "compliant"
            compliant += 1

        remediation = None
        if status == "gap" and evidence:
            remediation = "Remediate {} issue in {}".format(evidence[0].type, evidence[0].file)

        items.append(AuditItem(
            framework=framework,
            control_id=ctrl["control_id"],
            title=ctrl["title"],
            status=status,
            policy_citation=citation,
            evidence=evidence,
            remediation=remediation,
        ))

    return AuditReport(
        framework=framework,
        score="{}/{}".format(compliant, len(controls)),
        items=items,
    )


if __name__ == "__main__":
    report = run_audit("ISO 27001")
    print("Audit: {} — score {}".format(report.framework, report.score))
    for item in report.items:
        print("  [{}] {} {} — {} findings".format(
            item.status, item.control_id, item.title, len(item.evidence)))
