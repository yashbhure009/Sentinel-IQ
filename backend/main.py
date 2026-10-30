"""SentinelIQ FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import time

from pydantic import BaseModel

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


from backend.graph.live_scanner import run_checkov_live, run_nmap_live, run_socket_live


class ScanRequest(BaseModel):
    repo_path: str = "/tmp/acme-payments-demo"
    nmap_host: str = "127.0.0.1"
    use_socket: bool = False


@app.post("/scan")
def post_scan(req: ScanRequest):
    start = time.time()
    checkov_findings = run_checkov_live(req.repo_path)
    nmap_findings = run_nmap_live(req.nmap_host)
    socket_findings = run_socket_live(req.repo_path) if req.use_socket else []
    all_findings = checkov_findings + nmap_findings + socket_findings

    try:
        from backend.graph import router as graph_router_mod
        graph_router_mod._FINDINGS[:] = all_findings
    except Exception:
        pass

    return {
        "scanned_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_seconds": round(time.time() - start, 1),
        "total": len(all_findings),
        "breakdown": {
            "checkov": len(checkov_findings),
            "nmap": len(nmap_findings),
            "socket": len(socket_findings),
        },
        "repo_path": req.repo_path,
        "nmap_host": req.nmap_host,
        "sample": [f.model_dump() for f in all_findings[:10]],
    }


def _find_frontend():
    candidates = [
        Path(__file__).resolve().parent.parent / "frontend",
        Path.cwd() / "frontend",
        Path("/opt/render/project/src/frontend"),
    ]
    for c in candidates:
        if c.exists() and (c / "index.html").exists():
            return c
    return None


_FRONTEND = _find_frontend()

if _FRONTEND:
    app.mount("/static", StaticFiles(directory=str(_FRONTEND)), name="static")

    @app.get("/")
    def root():
        return FileResponse(str(_FRONTEND / "index.html"))
else:
    @app.get("/")
    def root_missing():
        return JSONResponse({"error": "frontend not found"}, status_code=503)
