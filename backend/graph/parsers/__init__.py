"""Aggregate all scan outputs into one [Finding] list."""
from pathlib import Path
from backend.schemas import Finding
from backend.graph.parsers.checkov_parser import parse_checkov
from backend.graph.parsers.pip_audit_parser import parse_pip_audit

SCANS_DIR = Path(__file__).resolve().parent.parent / "scans"


def load_all_findings():
    findings = []
    checkov_path = SCANS_DIR / "checkov_output.json"
    if checkov_path.exists():
        findings.extend(parse_checkov(str(checkov_path)))
    pip_audit_path = SCANS_DIR / "pip_audit.json"
    if pip_audit_path.exists():
        findings.extend(parse_pip_audit(str(pip_audit_path)))
    return findings


if __name__ == "__main__":
    fs = load_all_findings()
    print("Total findings: {}".format(len(fs)))
    from collections import Counter
    print("\nBy type:")
    for t, n in Counter(f.type for f in fs).most_common():
        print("  {}: {}".format(t, n))
    print("\nBy severity:")
    for s, n in Counter(f.severity for f in fs).most_common():
        print("  {}: {}".format(s, n))
    print("\nBy source:")
    for s, n in Counter(f.source for f in fs).most_common():
        print("  {}: {}".format(s, n))
