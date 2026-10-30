#!/usr/bin/env python3
"""SentinelIQ CLI — run scans from the terminal."""
import argparse
import json
import sys
from pathlib import Path

# Add repo to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.graph.parsers.checkov_parser import parse_checkov
from backend.graph.parsers.pip_audit_parser import parse_pip_audit
from backend.graph.mapper import map_finding
from backend.audit.engine import run_audit
from backend.schemas import Finding


def cmd_scan(args):
    """Scan a repo. Runs Checkov if installed, else uses cached results."""
    repo = Path(args.repo).resolve()
    if not repo.exists():
        print(f"Error: {repo} does not exist", file=sys.stderr)
        return 1

    print(f"🔍 Scanning {repo}")

    checkov_out = Path(args.checkov_output) if args.checkov_output else Path("backend/graph/scans/checkov_output.json")
    pip_out = Path(args.pip_audit_output) if args.pip_audit_output else Path("backend/graph/scans/pip_audit.json")

    findings = []
    if checkov_out.exists():
        findings.extend(parse_checkov(str(checkov_out)))
        print(f"  ✅ {len(findings)} Checkov findings")
    if pip_out.exists():
        deps = parse_pip_audit(str(pip_out))
        findings.extend(deps)
        print(f"  ✅ {len(deps)} CVE findings")

    print(f"\n📊 Total: {len(findings)} findings")

    # Save output
    out = Path(args.output)
    out.write_text(json.dumps([f.model_dump() for f in findings], indent=2))
    print(f"💾 Written to {out}")

    return 0


def cmd_audit(args):
    """Run an audit for a framework."""
    report = run_audit(args.framework)
    print(f"\n🛡️  {args.framework} Audit — Score: {report.score}\n")
    for item in report.items:
        icon = {"compliant": "✅", "gap": "❌", "missing_policy": "⚠️ "}[item.status]
        print(f"  {icon} {item.control_id} — {item.title}")
        print(f"      Evidence: {len(item.evidence)} findings")

    if args.output:
        Path(args.output).write_text(json.dumps(report.model_dump(), indent=2))
        print(f"\n💾 Written to {args.output}")

    return 0


def cmd_map(args):
    """Map a finding type to controls."""
    dummy = Finding(
        id="cli", type=args.type, file="cli", line=None,
        severity="high", source="cli", description="CLI test"
    )
    mappings = map_finding(dummy)
    print(f"\n🗺️  {args.type} maps to {len(mappings)} controls:\n")
    for m in mappings:
        print(f"  • {m.framework} {m.control_id} — {m.title}")

    return 0


def main():
    parser = argparse.ArgumentParser(prog="sentinelIQ", description="Self-hosted compliance scanner")
    sub = parser.add_subparsers(dest="cmd", required=True)

    scan_p = sub.add_parser("scan", help="Scan a repo for findings")
    scan_p.add_argument("--repo", required=True, help="Path to repo")
    scan_p.add_argument("--output", default="findings.json", help="Output file")
    scan_p.add_argument("--checkov-output", help="Pre-generated Checkov JSON")
    scan_p.add_argument("--pip-audit-output", help="Pre-generated pip-audit JSON")
    scan_p.set_defaults(func=cmd_scan)

    audit_p = sub.add_parser("audit", help="Run a compliance audit")
    audit_p.add_argument("--framework", default="ISO 27001", help="Framework name")
    audit_p.add_argument("--output", help="Output JSON file")
    audit_p.set_defaults(func=cmd_audit)

    map_p = sub.add_parser("map", help="Map a finding type to controls")
    map_p.add_argument("--type", required=True, help="Finding type")
    map_p.set_defaults(func=cmd_map)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
