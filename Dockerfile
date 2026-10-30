FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap git curl ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir checkov

COPY backend ./backend
COPY frontend ./frontend
COPY start.sh /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 10000

HEALTHCHECK --interval=30s --timeout=3s --start-period=90s \
    CMD curl -f http://localhost:${PORT:-10000}/health || exit 1

CMD ["/app/start.sh"]
