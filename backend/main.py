"""SentinelIQ FastAPI application entry point."""

from fastapi import FastAPI

app = FastAPI(title="SentinelIQ")

# TODO: Mount RAG, graph, and audit routers and configure frontend serving/CORS.


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a minimal service health response."""
    return {"status": "ok"}
