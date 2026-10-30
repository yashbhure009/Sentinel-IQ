#!/bin/bash
set -e

# Clone demo repo at startup (into writable location)
DEMO_REPO="/tmp/acme-payments-demo"
if [ ! -d "$DEMO_REPO" ]; then
  echo "[start] Cloning acme-payments-demo..."
  git clone --depth=1 https://github.com/Yash150406/acme-payments-demo.git "$DEMO_REPO" || \
    echo "[start] Clone failed (non-fatal, cached findings still work)"
  chmod -R a+rX "$DEMO_REPO" 2>/dev/null || true
fi

echo "[start] Demo repo ready:"
ls "$DEMO_REPO" 2>/dev/null | head -3

# Run the app
exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}
