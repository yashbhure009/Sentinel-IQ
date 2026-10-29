"""Parse Checkov JSON output to [Finding]."""
import json
from pathlib import Path
from backend.schemas import Finding

CHECKOV_MAP = {
    "CKV_AWS_41": "hardcoded_secret",
    "CKV_SECRET_2": "hardcoded_secret",
    "CKV_SECRET_6": "hardcoded_secret",
    "CKV_AWS_20": "public_s3_bucket",
    "CKV_AWS_57": "public_s3_bucket",
    "CKV2_AWS_6": "public_s3_bucket",
    "CKV_AWS_16": "unencrypted_storage",
    "CKV_AWS_17": "unencrypted_storage",
    "CKV_AWS_19": "unencrypted_storage",
    "CKV_AWS_145": "unencrypted_storage",
    "CKV_AWS_3": "unencrypted_storage",
    "CKV_AWS_189": "unencrypted_storage",
    "CKV_AWS_42": "unencrypted_storage",
    "CKV_AWS_184": "unencrypted_storage",
    "CKV2_AWS_2": "unencrypted_storage",
    "CKV_AWS_23": "open_security_group",
    "CKV_AWS_24": "open_security_group",
    "CKV_AWS_25": "open_security_group",
    "CKV_AWS_260": "open_security_group",
    "CKV_AWS_277": "open_security_group",
    "CKV_AWS_382": "open_security_group",
    "CKV2_AWS_5": "open_security_group",
    "CKV_AWS_62": "overly_permissive_iam",
    "CKV_AWS_63": "overly_permissive_iam",
    "CKV_AWS_286": "overly_permissive_iam",
    "CKV_AWS_287": "overly_permissive_iam",
    "CKV_AWS_288": "overly_permissive_iam",
    "CKV_AWS_289": "overly_permissive_iam",
    "CKV_AWS_290": "overly_permissive_iam",
    "CKV_AWS_355": "overly_permissive_iam",
    "CKV2_AWS_40": "overly_permissive_iam",
    "CKV_AWS_40": "overly_permissive_iam",
    "CKV_AWS_2": "weak_tls",
    "CKV_AWS_103": "weak_tls",
    "CKV_AWS_378": "weak_tls",
    "CKV2_AWS_20": "weak_tls",
    "CKV2_AWS_74": "weak_tls",
    "CKV_AWS_18": "missing_logging",
    "CKV_AWS_91": "missing_logging",
    "CKV_AWS_129": "missing_logging",
    "CKV_AWS_353": "missing_logging",
    "CKV2_AWS_30": "missing_logging",
    "CKV2_AWS_61": "missing_logging",
    "CKV2_AWS_62": "missing_logging",
    "CKV_DOCKER_2": "missing_logging",
    "CKV_DOCKER_3": "missing_logging",
    "CKV_DOCKER_7": "missing_logging",
}

NAME_HINTS = [
    ("public", "public_s3_bucket"),
    ("encrypt", "unencrypted_storage"),
    ("security group", "open_security_group"),
    ("ingress", "open_security_group"),
    ("wildcard", "overly_permissive_iam"),
    ("iam", "overly_permissive_iam"),
    ("tls", "weak_tls"),
    ("ssl", "weak_tls"),
    ("log", "missing_logging"),
    ("secret", "hardcoded_secret"),
    ("credential", "hardcoded_secret"),
]


def _map_type(check_id, check_name):
    if check_id in CHECKOV_MAP:
        return CHECKOV_MAP[check_id]
    name = (check_name or "").lower()
    for hint, ftype in NAME_HINTS:
        if hint in name:
            return ftype
    return None


def _severity(check_id, check_name):
    if check_id in ("CKV_SECRET_2", "CKV_SECRET_6", "CKV_AWS_41"):
        return "critical"
    if check_id in ("CKV_AWS_20", "CKV_AWS_57", "CKV_AWS_16", "CKV_AWS_17",
                    "CKV_AWS_3", "CKV_AWS_42", "CKV_AWS_62", "CKV_AWS_63"):
        return "high"
    name = (check_name or "").lower()
    if "secret" in name or "credential" in name:
        return "critical"
    if "public" in name or "encrypt" in name:
        return "high"
    if "ingress" in name or "security group" in name:
        return "high"
    return "medium"


def parse_checkov(path):
    data = json.loads(Path(path).read_text())
    reports = data if isinstance(data, list) else [data]
    findings = []
    seen = set()
    for report in reports:
        for check in report.get("results", {}).get("failed_checks", []):
            ftype = _map_type(check.get("check_id", ""), check.get("check_name", ""))
            if not ftype:
                continue
            file_path = check.get("file_path", "unknown")
            line_range = check.get("file_line_range") or [None, None]
            line = line_range[0] if isinstance(line_range, list) and line_range else None
            key = (ftype, file_path, line, check.get("resource"))
            if key in seen:
                continue
            seen.add(key)
            findings.append(Finding(
                id="c-{:03d}".format(len(findings) + 1),
                type=ftype,
                file=file_path,
                line=line,
                severity=_severity(check.get("check_id", ""), check.get("check_name", "")),
                source="checkov",
                description=check.get("check_name", ftype),
            ))
    return findings


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "backend/graph/scans/checkov_output.json"
    fs = parse_checkov(path)
    print("Parsed {} findings from {}".format(len(fs), path))
    from collections import Counter
    for t, n in Counter(f.type for f in fs).most_common():
        print("  {}: {}".format(t, n))
