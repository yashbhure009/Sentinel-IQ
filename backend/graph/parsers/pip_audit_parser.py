"""Parse pip_audit / OSV output to [Finding] of type vulnerable_dependency."""
import json
from pathlib import Path
from backend.schemas import Finding


def _severity(vuln):
    sev = (vuln.get("severity") or "").lower()
    if sev in ("critical", "high", "medium", "low"):
        return sev
    return "high"


def parse_pip_audit(path):
    data = json.loads(Path(path).read_text())
    deps = data.get("dependencies", data if isinstance(data, list) else [])
    findings = []
    for dep in deps:
        pkg = dep.get("name", "unknown")
        ver = dep.get("version", "?")
        for vuln in dep.get("vulns", []):
            vid = vuln.get("id", "CVE-UNKNOWN")
            summary = vuln.get("summary") or "{} in {} {}".format(vid, pkg, ver)
            findings.append(Finding(
                id="d-{:03d}".format(len(findings) + 1),
                type="vulnerable_dependency",
                file="app/requirements.txt",
                line=None,
                severity=_severity(vuln),
                source="osv",
                description="{}=={}: {}".format(pkg, ver, summary),
            ))
    return findings


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "backend/graph/scans/pip_audit.json"
    fs = parse_pip_audit(path)
    print("Parsed {} CVE findings from {}".format(len(fs), path))
    from collections import Counter
    pkgs = Counter(f.description.split("==")[0] for f in fs)
    for p, n in pkgs.most_common():
        print("  {}: {} CVEs".format(p, n))
