"""
CLIbrary demo web server.

Serves the static frontend and exposes:
  POST /api/route        — route a query through the selected backend
  GET  /api/benchmark    — return stored benchmark results
  GET  /api/health       — liveness check

Start:
    cd web && uvicorn app:app --reload --port 8000
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from clibrary_hub.router import CLIbrary
from clibrary_hub.reranker import Qwen3Reranker

app = FastAPI(title="CLIbrary Demo", version="0.2.0")

# ── Index paths ────────────────────────────────────────────────────────────────
_HOME = Path.home()
_INDEX_DIRS = {
    "e5":      _HOME / ".clibrary" / "indices_e5_small",
    "qwen":    _HOME / ".clibrary" / "indices_qwen_small",
    "e5_full": _HOME / ".clibrary" / "indices_e5",
}
_MODELS = {
    "e5":      "intfloat/multilingual-e5-base",
    "qwen":    "Qwen/Qwen3-Embedding-0.6B",
    "e5_full": "intfloat/multilingual-e5-base",
}

# Lazy caches — keyed by "backend" and "backend+reranker"
_routers:  dict[str, CLIbrary]     = {}
_reranker: Qwen3Reranker | None    = None

def _get_reranker() -> Qwen3Reranker:
    global _reranker
    if _reranker is None:
        _reranker = Qwen3Reranker()
    return _reranker

def get_router(backend: str, use_reranker: bool = False) -> CLIbrary:
    key = f"{backend}+reranker" if use_reranker else backend
    if key not in _routers:
        idx_dir = _INDEX_DIRS.get(backend)
        model   = _MODELS.get(backend)
        if idx_dir is None or not idx_dir.exists():
            raise HTTPException(status_code=503, detail=f"Index '{backend}' not built yet.")
        reranker = _get_reranker() if use_reranker else None
        _routers[key] = CLIbrary(index_dir=idx_dir, model_name=model, reranker=reranker)
    return _routers[key]


# ── Request / response models ──────────────────────────────────────────────────

class RouteRequest(BaseModel):
    query: str
    backend: Literal["e5", "qwen", "e5_full"] = "e5"
    use_reranker: bool = False

class RouteResponse(BaseModel):
    action: str
    cli: str | None = None
    description: str | None = None
    params: dict = {}
    confidence: float | None = None
    ex_score: float | None = None
    source: str | None = None
    rerank_method: str | None = None
    top3: list[dict] = []
    choices: list[dict] = []
    latency_ms: float = 0.0
    backend: str = ""


# ── API routes ─────────────────────────────────────────────────────────────────

@app.post("/api/route", response_model=RouteResponse)
def route(req: RouteRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    router = get_router(req.backend, req.use_reranker)
    result = router.route(req.query.strip())
    cli_meta = result.get("cli_meta", {})
    return RouteResponse(
        action=result["action"],
        cli=result.get("cli"),
        description=cli_meta.get("description", ""),
        params=result.get("params", {}),
        confidence=result.get("confidence"),
        ex_score=result.get("ex_score"),
        source=result.get("source"),
        rerank_method=result.get("rerank_method"),
        top3=result.get("top3", []),
        choices=result.get("choices", []),
        latency_ms=result.get("latency_ms", 0.0),
        backend=req.backend,
    )


@app.get("/api/benchmark")
def benchmark():
    results_path = Path(__file__).parent.parent / "benchmark" / "results.json"
    if not results_path.exists():
        return JSONResponse({"error": "No benchmark results yet. Run benchmark/run_eval.py first."}, status_code=404)
    return json.loads(results_path.read_text())


@app.get("/api/backends")
def backends():
    available = {k: v.exists() for k, v in _INDEX_DIRS.items()}
    return {"backends": available, "models": _MODELS}


@app.get("/api/health")
def health():
    return {"status": "ok", "timestamp": time.time()}


# ── Static files & SPA fallback ────────────────────────────────────────────────
_STATIC = Path(__file__).parent / "static"

app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")

@app.get("/")
def index():
    return FileResponse(str(_STATIC / "index.html"))
