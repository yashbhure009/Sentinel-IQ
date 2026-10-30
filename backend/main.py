"""SentinelIQ FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI(title="SentinelIQ")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.graph.router import router as graph_router
from backend.audit.router import router as audit_router
from backend.agents.registry import AGENTS

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


@app.get("/agents")
def list_agents():
    return [a.info() for a in AGENTS.values()]


@app.post("/agents/{name}/run")
def run_agent(name: str, context: dict = {}):
    agent = AGENTS.get(name)
    if not agent:
        return {"error": "unknown agent", "available": list(AGENTS.keys())}
    return agent.run(context)

import os

@app.get("/debug")
def debug_info():
    from pathlib import Path
    cwd = Path.cwd()
    file_dir = Path(__file__).resolve().parent
    parent = file_dir.parent
    frontend = parent / "frontend"
    return {
        "cwd": str(cwd),
        "main_py": str(Path(__file__).resolve()),
        "backend_dir": str(file_dir),
        "parent": str(parent),
        "frontend_path": str(frontend),
        "frontend_exists": frontend.exists(),
        "parent_contents": sorted(p.name for p in parent.iterdir()) if parent.exists() else [],
        "frontend_contents": sorted(p.name for p in frontend.iterdir()) if frontend.exists() else [],
    }
_FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
if _FRONTEND.exists():
    app.mount("/static", StaticFiles(directory=str(_FRONTEND)), name="static")

    @app.get("/")
    def root():
        return FileResponse(str(_FRONTEND / "index.html"))
