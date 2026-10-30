"""Live scanning — runs Checkov + Nmap (+ optional Socket) at runtime."""
import json
import os
import subprocess
import tempfile
from pathlib import Path
from backend.schemas import Finding


def run_checkov_live(target_path: str) -> list[Finding]:
    """Run Checkov live on a directory. Capture stdout directly."""
    from backend.graph.parsers.checkov_parser import parse_checkov

    target = Path(target_path).expanduser().resolve()
    if not target.exists():
        print(f"[live] checkov: target not found: {target}")
        return []

    try:
        result = subprocess.run(
            ["checkov", "-d", str(target), "-o", "json", "--compact"],
            capture_output=True, text=True, timeout=300,
        )
        print(f"[live] checkov rc={result.returncode} stdout={len(result.stdout)}B")

        if not result.stdout.strip():
            print(f"[live] checkov: empty stdout, stderr={result.stderr[:200]}")
            return []

        tmp_dir = tempfile.mkdtemp()
        tmp_file = Path(tmp_dir) / "checkov.json"
        tmp_file.write_text(result.stdout)

        findings = parse_checkov(str(tmp_file))
        print(f"[live] checkov: parsed {len(findings)} findings")
        return findings
    except subprocess.TimeoutExpired:
        print("[live] checkov: timeout after 5 min")
        return []
    except FileNotFoundError:
        print("[live] checkov: binary not found")
        return []
    except Exception as e:
        print(f"[live] checkov exception: {e}")
        return []



def run_nmap_live(host: str = "127.0.0.1") -> list[Finding]:
    """Run Nmap against a host. Returns open_port findings."""
    import nmap

    try:
        nm = nmap.PortScanner()
        nm.scan(hosts=host, arguments="-sT -T4 --top-ports 100")
        findings = []
        risky = {22: "high", 23: "critical", 21: "high", 445: "critical",
                 3306: "high", 5432: "high", 6379: "high", 3389: "critical",
                 27017: "high", 9200: "critical", 11211: "high",
                 8080: "medium", 8443: "medium", 10000: "low"}
        idx = 1
        for h in nm.all_hosts():
            for proto in nm[h].all_protocols():
                for port in nm[h][proto].keys():
                    info = nm[h][proto][port]
                    if info["state"] != "open":
                        continue
                    findings.append(Finding(
                        id=f"n-{idx:03d}",
                        type="open_port",
                        file=f"{h}:{port}",
                        line=None,
                        severity=risky.get(int(port), "medium"),
                        source="nmap",
                        description=f"Open port {port}/{proto} ({info.get('name', 'unknown')}) on {h}",
                    ))
                    idx += 1
        return findings
    except Exception as e:
        print(f"[live] nmap failed: {e}")
        return []


def run_socket_live(target_path: str) -> list[Finding]:
    """Run Socket CLI on a repo's dependencies. Requires SOCKET_API_KEY env var."""
    api_key = os.environ.get("SOCKET_API_KEY") or os.environ.get("SOCKET_SECURITY_API_KEY")
    if not api_key:
        print("[live] socket: no SOCKET_API_KEY env var, skipping")
        return []

    target = Path(target_path).expanduser().resolve()
    if not target.exists():
        return []

    try:
        result = subprocess.run(
            ["socket", "scan", "create", str(target), "--json"],
            capture_output=True, text=True, timeout=180,
            env={**os.environ, "SOCKET_API_KEY": api_key},
        )
        if result.returncode != 0 or not result.stdout.strip():
            print(f"[live] socket: failed (rc={result.returncode})")
            return []

        data = json.loads(result.stdout)
        issues = data.get("issues", data.get("data", {}).get("issues", []))
        findings = []
        for i, issue in enumerate(issues, 1):
            pkg = issue.get("package") or issue.get("purl", "unknown")
            sev = (issue.get("severity") or "high").lower()
            if sev not in ("low", "medium", "high", "critical"):
                sev = "high"
            findings.append(Finding(
                id=f"s-{i:03d}",
                type="vulnerable_dependency",
                file="requirements.txt",
                line=None,
                severity=sev,
                source="socket",
                description=f"{pkg}: {issue.get('title', issue.get('id', 'vuln'))}",
            ))
        return findings
    except subprocess.TimeoutExpired:
        print("[live] socket: timeout")
        return []
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[live] socket: {e}")
        return []
