#!/bin/bash
set -e

echo "[start] === SentinelIQ container startup ==="
echo "[start] Working dir: $(pwd)"

# Clone demo repo at startup
DEMO_REPO="/tmp/acme-payments-demo"
if [ ! -d "$DEMO_REPO/terraform" ]; then
  echo "[start] Cloning acme-payments-demo..."
  rm -rf "$DEMO_REPO"
  git clone --depth=1 https://github.com/Yash150406/acme-payments-demo.git "$DEMO_REPO" 2>&1 || \
    echo "[start] Clone failed — Checkov will return 0"
  chmod -R a+rX "$DEMO_REPO" 2>/dev/null || true
else
  echo "[start] Demo repo already present"
fi

echo "[start] Demo repo contents:"
ls -la "$DEMO_REPO" 2>/dev/null || echo "[start] (not found)"

echo "[start] Nmap check:"
which nmap || echo "[start] nmap NOT installed"
nmap --version 2>&1 | head -1 || true

echo "[start] Checkov check:"
which checkov || echo "[start] checkov NOT installed"

echo "[start] Starting uvicorn on port ${PORT:-10000}..."
exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}
