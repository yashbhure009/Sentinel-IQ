"""SentinelIQ FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SentinelIQ")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.graph.router import router as graph_router
from backend.audit.router import router as audit_router

app.include_router(graph_router)
app.include_router(audit_router)

try:
    from backend.rag.router import router as rag_router
    app.include_router(rag_router)
except Exception:
    pass


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
