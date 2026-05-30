"""
build_index.py — Build FAISS indices from CLI manifest files.

Reads manifest.json files under a directory tree, encodes them with
multilingual-e5-base, and writes three FAISS index files:

  cli_index.faiss     — one vector per CLI (mean of intent_triggers)
  trigger_index.faiss — one vector per trigger (MaxSim re-ranking)
  example_index.faiss — one vector per example query (Path A/B split)

Usage:
    python -m clibrary.build_index --manifest-dir ./manifests
    python -m clibrary.build_index --manifest-dir ./manifests --output-dir ./indices
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

PASSAGE_PREFIX = "passage: "
DEFAULT_MODEL = "intfloat/multilingual-e5-base"
DEFAULT_OUTPUT_DIR = Path.home() / ".clibrary" / "indices"

# Models that use prompt_name kwarg instead of a text prefix
_QWEN_MODELS = {"Qwen/Qwen3-Embedding", "Qwen/Qwen3-Embedding-0.6B"}


def load_manifests(manifest_dir: Path) -> list[dict]:
    manifests = []
    skipped = 0

    for manifest_file in sorted(manifest_dir.rglob("manifest.json")):
        try:
            with open(manifest_file, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  SKIP (read error): {manifest_file} — {e}", file=sys.stderr)
            skipped += 1
            continue

        if not data.get("intent_triggers"):
            print(f"  SKIP (no intent_triggers): {manifest_file.parent.name}", file=sys.stderr)
            skipped += 1
            continue

        manifests.append(data)

    if skipped:
        print(f"  Skipped {skipped} manifest(s) with errors.", file=sys.stderr)

    return manifests


def _encode_passages(model: SentenceTransformer, texts: list[str], model_name: str, **kwargs) -> "np.ndarray":
    """Encode passage texts, using prompt_name for Qwen models."""
    if model_name in _QWEN_MODELS:
        # Strip the "passage: " prefix we added — Qwen uses prompt_name="document"
        clean = [t.removeprefix(PASSAGE_PREFIX) for t in texts]
        return model.encode(clean, prompt_name="document", **kwargs)
    return model.encode(texts, **kwargs)


def build_indices(
    manifests: list[dict],
    model: SentenceTransformer,
    model_name: str = DEFAULT_MODEL,
) -> tuple[faiss.Index, list, faiss.Index, list, faiss.Index, list, int]:
    cli_meta: list[dict] = []
    trigger_meta: list[dict] = []
    example_meta: list[dict] = []

    cli_texts: list[str] = []
    cli_bounds: list[tuple[int, int]] = []
    trigger_texts: list[str] = []
    example_texts: list[str] = []

    for m in manifests:
        triggers = m.get("intent_triggers", [])

        start = len(cli_texts)
        cli_texts.extend([PASSAGE_PREFIX + t for t in triggers])
        cli_bounds.append((start, len(cli_texts)))

        for t in triggers:
            trigger_texts.append(PASSAGE_PREFIX + t)
            trigger_meta.append({"cli_name": m["name"], "trigger": t})

        for ex in m.get("examples", []):
            q = ex.get("query", ex.get("intent", ""))
            if q:
                example_texts.append(PASSAGE_PREFIX + q)
                example_meta.append({
                    "cli_name": m["name"],
                    "query": q,
                    "params": ex.get("params", {}),
                })

        cli_meta.append({
            "name": m["name"],
            "description": m.get("description", ""),
            "category": m.get("category", ""),
            "params_schema": m.get("input_schema", m.get("parameters", {})),
        })

    print(f"  Encoding {len(cli_texts)} trigger texts for cli_index...")
    t0 = time.perf_counter()
    all_trigger_vecs = _encode_passages(
        model, cli_texts, model_name,
        batch_size=64, show_progress_bar=True, normalize_embeddings=True,
    ).astype("float32")
    print(f"  Done ({time.perf_counter() - t0:.1f}s)")

    # Mean-pool triggers → one vector per CLI, then re-normalise
    dim = all_trigger_vecs.shape[1]
    cli_vecs = np.zeros((len(manifests), dim), dtype="float32")
    for i, (s, e) in enumerate(cli_bounds):
        cli_vecs[i] = all_trigger_vecs[s:e].mean(axis=0)
    norms = np.linalg.norm(cli_vecs, axis=1, keepdims=True)
    cli_vecs /= np.maximum(norms, 1e-9)

    print(f"  Encoding {len(example_texts)} example queries...")
    t0 = time.perf_counter()
    example_vecs = _encode_passages(
        model, example_texts, model_name,
        batch_size=64, show_progress_bar=True, normalize_embeddings=True,
    ).astype("float32")
    print(f"  Done ({time.perf_counter() - t0:.1f}s)")

    # FAISS IndexFlatIP — inner product == cosine on normalised vectors
    cli_index = faiss.IndexFlatIP(dim)
    cli_index.add(cli_vecs)

    trigger_index = faiss.IndexFlatIP(dim)
    trigger_index.add(all_trigger_vecs)

    example_index = faiss.IndexFlatIP(dim)
    example_index.add(example_vecs)

    return cli_index, cli_meta, trigger_index, trigger_meta, example_index, example_meta, dim


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Build FAISS indices for CLIbrary router.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m clibrary.build_index --manifest-dir ./manifests
  python -m clibrary.build_index --manifest-dir ./manifests --output-dir ./my_indices
  clibrary-build-index --manifest-dir ./manifests
        """,
    )
    parser.add_argument(
        "--manifest-dir",
        required=True,
        type=Path,
        help="Root directory containing manifest.json files (searched recursively).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to write .faiss and .json files (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Sentence-Transformers model ID (default: {DEFAULT_MODEL}).",
    )
    args = parser.parse_args(argv)

    manifest_dir: Path = args.manifest_dir
    output_dir: Path = args.output_dir

    if not manifest_dir.is_dir():
        print(f"Error: --manifest-dir '{manifest_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading manifests from: {manifest_dir}")
    manifests = load_manifests(manifest_dir)
    if not manifests:
        print("Error: No valid manifests found.", file=sys.stderr)
        sys.exit(1)
    print(f"  Loaded {len(manifests)} manifests\n")

    print(f"Loading model: {args.model}")
    t0 = time.perf_counter()
    model = SentenceTransformer(args.model)
    print(f"  Done ({time.perf_counter() - t0:.1f}s)\n")

    cli_idx, cli_meta, trig_idx, trig_meta, ex_idx, ex_meta, dim = build_indices(
        manifests, model, model_name=args.model
    )

    print(f"\nWriting indices to: {output_dir}")
    faiss.write_index(cli_idx, str(output_dir / "cli_index.faiss"))
    faiss.write_index(trig_idx, str(output_dir / "trigger_index.faiss"))
    faiss.write_index(ex_idx, str(output_dir / "example_index.faiss"))

    with open(output_dir / "cli_meta.json", "w", encoding="utf-8") as f:
        json.dump(cli_meta, f, ensure_ascii=False, indent=2)
    with open(output_dir / "trigger_meta.json", "w", encoding="utf-8") as f:
        json.dump(trig_meta, f, ensure_ascii=False, indent=2)
    with open(output_dir / "example_meta.json", "w", encoding="utf-8") as f:
        json.dump(ex_meta, f, ensure_ascii=False, indent=2)

    model_info = {
        "model": args.model,
        "vector_dim": dim,
        "cli_count": len(cli_meta),
        "trigger_count": len(trig_meta),
        "example_count": len(ex_meta),
        "manifest_dir": str(manifest_dir.resolve()),
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    with open(output_dir / "model_info.json", "w", encoding="utf-8") as f:
        json.dump(model_info, f, indent=2)

    print(f"\nDone.")
    print(f"  CLIs:     {len(cli_meta)}  ({dim}d vectors)")
    print(f"  Triggers: {len(trig_meta)}")
    print(f"  Examples: {len(ex_meta)}")
    print(f"  Output:   {output_dir}")


if __name__ == "__main__":
    main()
