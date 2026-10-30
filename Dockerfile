FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap git curl ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir checkov

RUN git clone --depth=1 https://github.com/Yash150406/acme-payments-demo.git /tmp/acme-payments-demo && \
    chmod -R a+rX /tmp/acme-payments-demo

COPY backend ./backend
COPY frontend ./frontend

RUN useradd -m -u 1000 sentinel && chown -R sentinel:sentinel /app
USER sentinel

EXPOSE 10000

HEALTHCHECK --interval=30s --timeout=3s --start-period=60s \
    CMD curl -f http://localhost:${PORT:-10000}/health || exit 1

CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}
