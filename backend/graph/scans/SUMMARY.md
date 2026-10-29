# Scan Summary — acme-payments-demo

Source repo: github.com/Yash150406/acme-payments-demo
(public, intentionally vulnerable, fake AWS dummies only)

## Raw scan outputs

- `checkov_output.json` — Checkov 3.3.30, 103 failed checks (99 Terraform + 2 Dockerfile + 2 Secrets)
- `pip_audit.json` — OSV.dev, 100 CVEs across 7 packages

## Parsed findings (136 total)

| Type | Count |
|---|---|
| vulnerable_dependency | 100 |
| missing_logging | 8 |
| unencrypted_storage | 8 |
| overly_permissive_iam | 5 |
| public_s3_bucket | 5 |
| weak_tls | 4 |
| hardcoded_secret | 3 |
| open_security_group | 3 |

## Severity breakdown

- high: 116
- medium: 17
- critical: 3

## Finding schema

```python
Finding(
    id: str,
    type: Literal[
        "hardcoded_secret", "vulnerable_dependency", "public_s3_bucket",
        "open_security_group", "weak_tls", "unencrypted_storage",
        "overly_permissive_iam", "missing_logging", "open_port",
    ],
    file: str,
    line: Optional[int],
    severity: Literal["low", "medium", "high", "critical"],
    source: str,
    description: str,
)
