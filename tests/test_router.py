"""
test_router.py — Unit tests for CLIbrary router

These tests use a minimal mock index and do not require FAISS or real embeddings.
For integration tests with the full index, see tests/test_integration.py.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from clibrary.manifest import load_manifest, validate_manifest, ManifestError


# ── Manifest tests ─────────────────────────────────────────────────────────────

def test_validate_manifest_valid():
    manifest = {
        "name": "csv-stat",
        "description": "CSV statistics calculator",
        "intent_triggers": ["analyze csv", "csv stats", "csv statistics"],
        "input_schema": {"type": "object", "properties": {"file": {"type": "string"}}},
        "examples": [{"query": "analyze sales.csv", "params": {"file": "sales.csv"}}],
    }
    errors = validate_manifest(manifest)
    assert errors == []


def test_validate_manifest_missing_fields():
    errors = validate_manifest({"name": "csv-stat"})
    assert any("Missing required fields" in e for e in errors)


def test_validate_manifest_too_few_triggers():
    manifest = {
        "name": "csv-stat",
        "description": "desc",
        "intent_triggers": ["only one trigger"],
        "input_schema": {},
    }
    errors = validate_manifest(manifest)
    assert any("intent_triggers" in e for e in errors)


def test_validate_manifest_example_missing_query():
    manifest = {
        "name": "csv-stat",
        "description": "desc",
        "intent_triggers": ["a", "b", "c"],
        "input_schema": {},
        "examples": [{"params": {"file": "x.csv"}}],  # missing query
    }
    errors = validate_manifest(manifest)
    assert any("query" in e for e in errors)


def test_load_manifest_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_manifest("/nonexistent/path/manifest.json")


# ── Router smoke tests (mocked) ────────────────────────────────────────────────

def _make_mock_router():
    """Build a CLIbrary instance with all FAISS/model state mocked out."""
    from clibrary.router import CLIbrary

    router = CLIbrary.__new__(CLIbrary)
    router._index_dir = None
    router._model_name = "mock"
    router._cli_top_k = 3
    router._example_threshold = 0.85
    router._clarify_min_score = 0.82
    router._clarify_min_gap = 0.010
    router._rerank_alpha = 0.7
    router._llm_backend = None

    # Minimal mock state
    router._model = MagicMock()
    router._model.encode.return_value = np.ones((1, 4), dtype="float32")

    router._cli_meta = [
        {"name": "csv-stat", "description": "CSV statistics"},
        {"name": "term-plot", "description": "Terminal plot"},
        {"name": "csv-sql", "description": "SQL on CSV"},
    ]
    router._trigger_meta = []
    router._example_meta = [
        {"cli_name": "csv-stat", "query": "analyze csv", "params": {"file": "data.csv"}},
    ]

    # Mock FAISS index
    mock_cli_index = MagicMock()
    mock_cli_index.search.return_value = (
        np.array([[0.95, 0.88, 0.75]], dtype="float32"),
        np.array([[0, 1, 2]]),
    )
    router._cli_index = mock_cli_index

    mock_example_index = MagicMock()
    mock_example_index.d = 4
    mock_example_index.reconstruct = lambda i, buf: buf.__setitem__(slice(None), np.ones(4, dtype="float32"))
    router._example_index = mock_example_index

    router._trigger_index = None
    router._trigger_by_cli = {}
    router._example_by_cli = {"csv-stat": [(0, router._example_meta[0])]}

    return router


def test_router_route_returns_action_route():
    router = _make_mock_router()
    result = router.route("analyze my csv file")
    assert result["action"] == "route"
    assert result["cli"] == "csv-stat"
    assert "confidence" in result
    assert "latency_ms" in result


def test_router_route_path_a():
    """High example similarity → Path A, no LLM call."""
    router = _make_mock_router()
    result = router.route("show me stats for data.csv")
    # Mock returns identical vectors → sim=1.0 → Path A
    assert result["source"] == "A"


def test_router_clarify_on_low_confidence():
    router = _make_mock_router()
    # Set scores too close and too low
    router._cli_index.search.return_value = (
        np.array([[0.80, 0.799, 0.75]], dtype="float32"),
        np.array([[0, 1, 2]]),
    )
    result = router.route("something ambiguous")
    assert result["action"] == "clarify"
    assert "choices" in result
    assert len(result["choices"]) > 0
