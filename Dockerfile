FROM python:3.11-slim

WORKDIR /app

# System deps: nmap binary + git for cloning target + curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap git curl && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir checkov

# Clone the demo repo for live scanning (runs at build time)
RUN git clone --depth=1 https://github.com/Yash150406/acme-payments-demo.git /tmp/acme-payments-demo || true

# App code
COPY backend ./backend
COPY frontend ./frontend

# Non-root user (add nmap capability via CAP_NET_RAW)
RUN useradd -m -u 1000 sentinel && chown -R sentinel:sentinel /app && \
    chmod +x /tmp/acme-payments-demo 2>/dev/null || true
USER sentinel

# Render injects $PORT at runtime — default to 10000 if unset
ENV PORT=10000
EXPOSE $PORT

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s CMD curl -f http://localhost:${PORT}/health || exit 1

# Use shell form so $PORT expands
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}
