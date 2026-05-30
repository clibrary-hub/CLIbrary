"""
router.py — Two-stage CLI routing core (offline, no external API calls)

Stage 1 : FAISS cli_index (mean-pooled triggers) → top-3 candidates
Re-rank : MaxSim over trigger_index to reorder top-3
Stage 2 : Find closest example within the winning CLI's example_index
Path A  : example similarity >= threshold → fill template
Path B  : example similarity < threshold → return empty params
          (the agent / caller decides how to fill them)
Clarify : top-1 score too low AND gap too small → return top-3 choices

This module makes no network calls. Param extraction for Path B is
intentionally left to the caller.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ── Defaults ──────────────────────────────────────────────────────────────────
_DEFAULT_CLI_TOP_K         = 3
_DEFAULT_EXAMPLE_THRESHOLD = 0.85   # >= this → Path A
_DEFAULT_CLARIFY_MIN_SCORE = 0.82   # top-1 below this + small gap → clarify
_DEFAULT_CLARIFY_MIN_GAP   = 0.010  # top1 - top2 gap below this (when low score) → clarify
_DEFAULT_RERANK_ALPHA      = 0.7    # combined = alpha*mean_sim + (1-alpha)*max_sim
_DEFAULT_MODEL             = "intfloat/multilingual-e5-base"
_QUERY_PREFIX              = "query: "

# Per-model query prefix overrides
_MODEL_QUERY_PREFIXES: dict[str, str] = {
    "Qwen/Qwen3-Embedding": "",   # Qwen3 uses prompt_name kwarg, not a text prefix
    "Qwen/Qwen3-Embedding-0.6B": "",
}
# ──────────────────────────────────────────────────────────────────────────────


class CLIbrary:
    """
    Two-stage retrieval router for CLI tool selection.

    Parameters
    ----------
    index_dir : str | Path | None
        Directory containing FAISS indices and metadata JSON files.
        Defaults to the bundled index shipped with the package.
    model_name : str
        Sentence-Transformers model for encoding queries.
    cli_top_k : int
        Number of candidate CLIs retrieved in Stage 1.
    example_threshold : float
        Cosine similarity cutoff for Path A (template reuse, no LLM).
    clarify_min_score : float
        If top-1 score is below this AND gap is small, return "clarify" action.
    clarify_min_gap : float
        Minimum score gap between top-1 and top-2 to avoid clarify.
    rerank_alpha : float
        Weight of mean_sim vs max_sim in re-ranking formula (ignored when reranker is set).
    reranker : object | None
        Optional Qwen3Reranker (or any object with a .rerank(query, candidates) method).
        When provided, replaces the MaxSim heuristic for Stage 1 re-ranking.
    """

    def __init__(
        self,
        index_dir: str | Path | None = None,
        model_name: str = _DEFAULT_MODEL,
        cli_top_k: int = _DEFAULT_CLI_TOP_K,
        example_threshold: float = _DEFAULT_EXAMPLE_THRESHOLD,
        clarify_min_score: float = _DEFAULT_CLARIFY_MIN_SCORE,
        clarify_min_gap: float = _DEFAULT_CLARIFY_MIN_GAP,
        rerank_alpha: float = _DEFAULT_RERANK_ALPHA,
        reranker: Any = None,
    ) -> None:
        self._index_dir = Path(index_dir) if index_dir else Path(__file__).parent / "indices"
        self._model_name = model_name
        self._cli_top_k = cli_top_k
        self._example_threshold = example_threshold
        self._clarify_min_score = clarify_min_score
        self._clarify_min_gap = clarify_min_gap
        self._rerank_alpha = rerank_alpha
        self._reranker = reranker

        # Lazy-loaded state
        self._model: SentenceTransformer | None = None
        self._cli_index: faiss.Index | None = None
        self._trigger_index: faiss.Index | None = None
        self._example_index: faiss.Index | None = None
        self._cli_meta: list[dict] = []
        self._trigger_meta: list[dict] = []
        self._example_meta: list[dict] = []
        self._trigger_by_cli: dict[str, list[int]] = {}
        self._example_by_cli: dict[str, list[tuple[int, dict]]] = {}

    # ── Lazy loading ──────────────────────────────────────────────────────────

    def _load(self) -> None:
        if self._model is not None:
            return

        idx = self._index_dir
        if not (idx / "cli_index.faiss").exists():
            raise RuntimeError(
                f"Index not found at {idx}. "
                "Run `python -m clibrary.build_index` to build indices first."
            )

        self._model = SentenceTransformer(self._model_name)
        self._cli_index = faiss.read_index(str(idx / "cli_index.faiss"))
        self._example_index = faiss.read_index(str(idx / "example_index.faiss"))

        trigger_path = idx / "trigger_index.faiss"
        if trigger_path.exists():
            self._trigger_index = faiss.read_index(str(trigger_path))

        with open(idx / "cli_meta.json", encoding="utf-8") as f:
            self._cli_meta = json.load(f)
        with open(idx / "example_meta.json", encoding="utf-8") as f:
            self._example_meta = json.load(f)

        trigger_meta_path = idx / "trigger_meta.json"
        if trigger_meta_path.exists():
            with open(trigger_meta_path, encoding="utf-8") as f:
                self._trigger_meta = json.load(f)
            for i, tm in enumerate(self._trigger_meta):
                self._trigger_by_cli.setdefault(tm["cli_name"], []).append(i)

        for i, em in enumerate(self._example_meta):
            self._example_by_cli.setdefault(em["cli_name"], []).append((i, em))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _encode(self, text: str) -> np.ndarray:
        assert self._model is not None
        # Qwen3-Embedding uses prompt_name kwarg instead of a text prefix
        if self._model_name in _MODEL_QUERY_PREFIXES:
            return self._model.encode(
                [text],
                prompt_name="query",
                normalize_embeddings=True,
                show_progress_bar=False,
            ).astype("float32")
        return self._model.encode(
            [_QUERY_PREFIX + text],
            normalize_embeddings=True,
            show_progress_bar=False,
        ).astype("float32")

    def _maxsim(self, cli_name: str, q_vec: np.ndarray) -> float:
        """Max cosine similarity between query and all triggers of a CLI."""
        if self._trigger_index is None:
            return 0.0
        indices = self._trigger_by_cli.get(cli_name, [])
        if not indices:
            return 0.0
        t_vecs = np.zeros((len(indices), self._trigger_index.d), dtype="float32")
        for row, gidx in enumerate(indices):
            self._trigger_index.reconstruct(gidx, t_vecs[row])
        return float((t_vecs @ q_vec.T).flatten().max())

    # ── Public API ────────────────────────────────────────────────────────────

    def route(self, query: str) -> dict[str, Any]:
        """
        Route a natural language query to the appropriate CLI tool.

        Returns one of two response shapes:

        Route response::

            {
                "action": "route",
                "cli": "csv-stat",
                "cli_meta": {...},
                "params": {"file": "data.csv"},
                "confidence": 0.94,
                "ex_score": 0.91,
                "source": "A",        # "A" = template, "B" = LLM
                "top3": [{"name": ..., "score": ...}, ...],
                "latency_ms": 36.2
            }

        Clarify response (low confidence)::

            {
                "action": "clarify",
                "choices": [{"name": ..., "description": ...}, ...],
                "latency_ms": 34.1
            }
        """
        t0 = time.perf_counter()
        self._load()

        # Stage 1: FAISS mean-sim retrieval
        q_vec = self._encode(query)
        raw_scores, raw_indices = self._cli_index.search(q_vec, self._cli_top_k)
        raw_scores = raw_scores[0].tolist()
        raw_indices = raw_indices[0].tolist()

        candidates = [
            (idx, mean_sim)
            for idx, mean_sim in zip(raw_indices, raw_scores)
            if idx >= 0
        ]

        if self._reranker is not None:
            # Cross-encoder reranking: replace MaxSim with Qwen3-Reranker scores
            idx_list = [idx for idx, _ in candidates]
            cand_metas = [self._cli_meta[idx] for idx in idx_list]
            ranked_pairs = self._reranker.rerank(query, cand_metas)
            # Build a name→faiss_idx lookup to avoid list.index() scan
            name_to_idx = {self._cli_meta[idx]["name"]: idx for idx in idx_list}
            reranked = [
                (name_to_idx[meta["name"]], 0.0, 0.0, score)
                for meta, score in ranked_pairs
            ]
            rerank_method = "cross-encoder"
        else:
            # Default MaxSim heuristic
            scored = []
            for idx, mean_sim in candidates:
                name = self._cli_meta[idx]["name"]
                max_sim = self._maxsim(name, q_vec)
                combined = self._rerank_alpha * mean_sim + (1 - self._rerank_alpha) * max_sim
                scored.append((idx, mean_sim, max_sim, combined))
            reranked = sorted(scored, key=lambda x: x[3], reverse=True)
            rerank_method = "maxsim"

        top3 = [
            {"name": self._cli_meta[idx]["name"], "score": round(combined, 4)}
            for idx, _, _, combined in reranked
        ]

        best_idx = reranked[0][0]
        best_score = reranked[0][3]
        second_score = reranked[1][3] if len(reranked) > 1 else 0.0
        best_cli_meta = self._cli_meta[best_idx]
        cli_name = best_cli_meta["name"]

        # Clarify check — reranker outputs p(yes) probabilities, not cosine similarities,
        # so use a much lower threshold (0.3) when a cross-encoder is active.
        clarify_threshold = 0.30 if self._reranker is not None else self._clarify_min_score
        clarify_gap = 0.05 if self._reranker is not None else self._clarify_min_gap
        if best_score < clarify_threshold and (best_score - second_score) < clarify_gap:
            return {
                "action": "clarify",
                "choices": [
                    {"name": self._cli_meta[idx]["name"], "description": self._cli_meta[idx].get("description", "")}
                    for idx, *_ in reranked
                ],
                "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            }

        # Stage 2: Example matching
        ex_entries = self._example_by_cli.get(cli_name, [])
        best_ex_score = 0.0
        best_params: dict[str, Any] = {}

        if ex_entries:
            ex_indices = [i for i, _ in ex_entries]
            ex_vecs = np.zeros((len(ex_indices), self._example_index.d), dtype="float32")
            for row, gidx in enumerate(ex_indices):
                self._example_index.reconstruct(gidx, ex_vecs[row])
            sims = (ex_vecs @ q_vec.T).flatten()
            best_row = int(sims.argmax())
            best_ex_score = float(sims[best_row])
            best_params = ex_entries[best_row][1]["params"]

        # Path A / B split — Path B returns empty params (no API call here).
        # Caller can fill them with their own logic / LLM if desired.
        source = "A" if best_ex_score >= self._example_threshold else "B"
        params = best_params if source == "A" else {}

        return {
            "action": "route",
            "cli": cli_name,
            "cli_meta": best_cli_meta,
            "params": params,
            "confidence": round(best_score, 4),
            "ex_score": round(best_ex_score, 4),
            "source": source,
            "rerank_method": rerank_method,
            "top3": top3,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
        }
