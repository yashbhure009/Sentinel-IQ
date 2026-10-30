# SentinelIQ Installation

Self-hosted compliance scanner. All data stays on your machine.

## Option A: Docker (recommended)

    git clone https://github.com/yashbhure009/Sentinel-IQ.git
    cd Sentinel-IQ
    docker compose up

Open http://localhost:8000.

## Option B: Python

    git clone https://github.com/yashbhure009/Sentinel-IQ.git
    cd Sentinel-IQ
    pip install -r requirements.txt
    pip install checkov
    uvicorn backend.main:app --port 8000

## Option C: CLI only

    pip install -e .
    sentinelIQ scan --repo /path/to/your/repo
    sentinelIQ audit --framework "ISO 27001"

## Scanning a repo

Point at any repo containing:
- Terraform (`*.tf`)
- Dockerfile / docker-compose.yml
- Python `requirements.txt`

Pre-generate scans:

    cd /path/to/repo
    checkov -d . -o json --output-file-path . --output-file checkov.json
    pip-audit -r requirements.txt -f json -o pip_audit.json

Then:

    sentinelIQ scan --repo . --checkov-output checkov.json --pip-audit-output pip_audit.json

## Supported frameworks

- ISO/IEC 27001:2022
- NIST SP 800-53
- SOC 2
- CIS Controls v8
- PCI DSS 4.0
- HIPAA Security Rule
- GDPR

## Data privacy

SentinelIQ does NOT send any data to external servers by default.
- Scans run locally
- Findings stored in local JSON
- LLM optional (uses Ollama by default — set `LLM_BACKEND=ollama`)

## Air-gapped mode

    NO_EGRESS=1 uvicorn backend.main:app

Refuses all outbound network calls. For air-gapped environments.

## Architecture

- Backend: FastAPI (`backend/main.py`)
- Frontend: Static HTML/JS (`frontend/`)
- Parsers: `backend/graph/parsers/`
- Ontology: `backend/graph/ontology.json` + `backend/audit/frameworks.json`
- Agents: `backend/agents/` (8 agents, 4 real + 4 scaffolded)
