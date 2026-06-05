#!/usr/bin/env python3
"""
build_index.py — WP-2: 建立 FAISS 向量索引
讀取 500 個 CLI manifest，用 multilingual-e5-base 向量化，存成三個 FAISS 索引：
  - cli_index.faiss     : 每個 CLI 一條向量（intent_triggers 平均，用於 Stage 1）
  - trigger_index.faiss : 每條 trigger 一條向量（用於 MaxSim re-ranking）
  - example_index.faiss : 每條 example.query 一條向量（用於 Stage 2）

用法：
    python poc/build_index.py
"""

import json
import time
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

CLI_ROOT  = Path(__file__).parent.parent / "manifests"
OUT_DIR   = Path(__file__).parent
MODEL_ID  = "intfloat/multilingual-e5-base"

# e5 模型需要加前綴
QUERY_PREFIX   = "query: "
PASSAGE_PREFIX = "passage: "


def iter_manifest_paths(cli_root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in sorted(cli_root.rglob("*.json")):
        if path.name == "manifest.json" or path.parent.name in {
            "ai-ml",
            "devops",
            "data",
            "web",
            "security",
            "media",
            "productivity",
            "finance",
            "science",
            "networking",
        }:
            paths.append(path)
    return paths


def load_manifests(cli_root: Path) -> list[dict]:
    manifests = []
    for mf in iter_manifest_paths(cli_root):
        with open(mf, encoding="utf-8") as f:
            data = json.load(f)
        if "intent_triggers" not in data:
            print(f"  SKIP (no intent_triggers): {mf}")
            continue
        data["_path"] = str(mf.relative_to(cli_root))
        manifests.append(data)
    return manifests


def build_indexes(manifests: list[dict], model: SentenceTransformer):
    cli_meta     = []
    example_meta = []
    cli_texts    = []   # 每個 CLI 的 trigger 文字（一批）
    cli_bounds   = []   # (start, end) 在 cli_texts 裡的位置
    example_texts = []

    for m in manifests:
        triggers = m.get("intent_triggers", [])
        start = len(cli_texts)
        cli_texts.extend([PASSAGE_PREFIX + t for t in triggers])
        cli_bounds.append((start, len(cli_texts)))

        for ex in m.get("examples", []):
            example_query = ex.get("query") or ex.get("intent") or ""
            example_texts.append(PASSAGE_PREFIX + example_query)
            example_meta.append({
                "cli_name": m["name"],
                "query":    example_query,
                "params":   ex.get("params", {}),
                "invocation": ex.get("invocation", ""),
            })

        cli_meta.append({
            "name":        m["name"],
            "description": m.get("description", ""),
            "category":    m.get("category", ""),
            "number":      m.get("number", 0),
            "pain_point":  m.get("pain_point", ""),
            "params_schema": m.get("params_schema") or m.get("input_schema", {}),
            "input_schema": m.get("input_schema", {}),
        })

    # trigger_meta：每條 trigger 對應的 CLI 名稱
    trigger_meta = []
    for m, (s, e) in zip(manifests, cli_bounds):
        for t in m.get("intent_triggers", []):
            trigger_meta.append({"cli_name": m["name"], "trigger": t})

    print(f"向量化 {len(cli_texts)} 條 trigger texts...")
    t0 = time.perf_counter()
    all_trigger_vecs = model.encode(
        cli_texts, batch_size=64, show_progress_bar=True,
        normalize_embeddings=True
    )
    print(f"  完成，耗時 {time.perf_counter()-t0:.1f}s")

    # 每個 CLI 取 triggers 的均值向量
    dim = all_trigger_vecs.shape[1]
    cli_vecs = np.zeros((len(manifests), dim), dtype="float32")
    for i, (s, e) in enumerate(cli_bounds):
        cli_vecs[i] = all_trigger_vecs[s:e].mean(axis=0)
    # re-normalize after mean
    norms = np.linalg.norm(cli_vecs, axis=1, keepdims=True)
    cli_vecs = cli_vecs / np.maximum(norms, 1e-9)

    print(f"向量化 {len(example_texts)} 條 example queries...")
    t0 = time.perf_counter()
    example_vecs = model.encode(
        example_texts, batch_size=64, show_progress_bar=True,
        normalize_embeddings=True
    ).astype("float32")
    print(f"  完成，耗時 {time.perf_counter()-t0:.1f}s")

    # FAISS IndexFlatIP（內積 = cosine，因為已 normalize）
    cli_index = faiss.IndexFlatIP(dim)
    cli_index.add(cli_vecs)

    # trigger_index：每條 trigger 獨立一個向量（用於 MaxSim re-ranking）
    trigger_vecs = all_trigger_vecs.astype("float32")
    trigger_index = faiss.IndexFlatIP(dim)
    trigger_index.add(trigger_vecs)

    example_index = faiss.IndexFlatIP(dim)
    example_index.add(example_vecs)

    return cli_index, cli_meta, trigger_index, trigger_meta, example_index, example_meta, dim


def main():
    OUT_DIR.mkdir(exist_ok=True)

    print("載入 manifest...")
    manifests = load_manifests(CLI_ROOT)
    print(f"  共 {len(manifests)} 個 CLI\n")

    print(f"載入模型 {MODEL_ID}...")
    t0 = time.perf_counter()
    model = SentenceTransformer(MODEL_ID)
    print(f"  完成，耗時 {time.perf_counter()-t0:.1f}s\n")

    cli_index, cli_meta, trigger_index, trigger_meta, example_index, example_meta, dim = build_indexes(manifests, model)

    # 存檔
    faiss.write_index(cli_index,     str(OUT_DIR / "cli_index.faiss"))
    faiss.write_index(trigger_index, str(OUT_DIR / "trigger_index.faiss"))
    faiss.write_index(example_index, str(OUT_DIR / "example_index.faiss"))

    with open(OUT_DIR / "cli_meta.json",     "w", encoding="utf-8") as f:
        json.dump(cli_meta,     f, ensure_ascii=False, indent=2)
    with open(OUT_DIR / "trigger_meta.json", "w", encoding="utf-8") as f:
        json.dump(trigger_meta, f, ensure_ascii=False, indent=2)
    with open(OUT_DIR / "example_meta.json", "w", encoding="utf-8") as f:
        json.dump(example_meta, f, ensure_ascii=False, indent=2)

    model_info = {
        "model":          MODEL_ID,
        "vector_dim":     dim,
        "cli_count":      len(cli_meta),
        "trigger_count":  len(trigger_meta),
        "example_count":  len(example_meta),
        "built_at":       time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(OUT_DIR / "model_info.json", "w", encoding="utf-8") as f:
        json.dump(model_info, f, indent=2)

    print(f"\n索引建立完成")
    print(f"  CLI 向量：{len(cli_meta)} 條  ({dim}d)")
    print(f"  Trigger 向量：{len(trigger_meta)} 條  (MaxSim re-ranking 用)")
    print(f"  Example 向量：{len(example_meta)} 條")
    print(f"  輸出目錄：{OUT_DIR}")


if __name__ == "__main__":
    main()
