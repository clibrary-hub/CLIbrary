#!/usr/bin/env python3
"""
router.py — 兩階段 CLI 路由核心（含 MaxSim re-ranking + 澄清介面）

Stage 1 : FAISS cli_index（mean-pooled triggers）→ top-3 候選
Re-rank : 對 top-3 用 trigger_index 做 MaxSim，重新排序
Stage 2 : 在命中 CLI 的 examples 中找最像的 example
分流    : example similarity >= EXAMPLE_THRESHOLD → A 路
          otherwise                               → B 路（Kimi API）
澄清    : top1-top2 分數差距太小 or top1 分數太低 → 問用戶

用法：
    python poc/router.py "查上週銷售總額"
"""

import json
import os
import sys
import time
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

POC_DIR = Path(__file__).parent

# ── 閾值 ──────────────────────────────────────────────────────────────────────
CLI_TOP_K            = 3
EXAMPLE_THRESHOLD    = 0.85   # >= 這個走 A 路
CLARIFY_MIN_SCORE    = 0.82   # top1 低於此（同時 gap 也小）→ 澄清
CLARIFY_MIN_GAP      = 0.010  # top1 - top2 差距低於此（同時分數也低）→ 澄清
RERANK_ALPHA         = 0.7    # combined = alpha*mean_sim + (1-alpha)*max_sim
QUERY_PREFIX         = "query: "
# ──────────────────────────────────────────────────────────────────────────────

_model          = None
_cli_index      = None
_trigger_index  = None
_example_index  = None
_cli_meta       = None
_trigger_meta   = None
_example_meta   = None
_trigger_by_cli: dict = {}
_example_by_cli: dict = {}


def _load():
    global _model, _cli_index, _trigger_index, _example_index
    global _cli_meta, _trigger_meta, _example_meta
    global _trigger_by_cli, _example_by_cli

    if _model is not None:
        return

    info_path = POC_DIR / "model_info.json"
    if not info_path.exists():
        raise RuntimeError("找不到索引，請先執行 python poc/build_index.py")

    with open(info_path) as f:
        info = json.load(f)

    _model         = SentenceTransformer(info["model"])
    _cli_index     = faiss.read_index(str(POC_DIR / "cli_index.faiss"))
    _example_index = faiss.read_index(str(POC_DIR / "example_index.faiss"))

    trigger_path = POC_DIR / "trigger_index.faiss"
    if trigger_path.exists():
        _trigger_index = faiss.read_index(str(trigger_path))

    with open(POC_DIR / "cli_meta.json",     encoding="utf-8") as f:
        _cli_meta = json.load(f)
    with open(POC_DIR / "example_meta.json", encoding="utf-8") as f:
        _example_meta = json.load(f)

    trigger_meta_path = POC_DIR / "trigger_meta.json"
    if trigger_meta_path.exists():
        with open(trigger_meta_path, encoding="utf-8") as f:
            _trigger_meta = json.load(f)
        for idx, tm in enumerate(_trigger_meta):
            _trigger_by_cli.setdefault(tm["cli_name"], []).append(idx)

    for idx, em in enumerate(_example_meta):
        _example_by_cli.setdefault(em["cli_name"], []).append((idx, em))


def _encode_query(text: str) -> np.ndarray:
    return _model.encode(
        [QUERY_PREFIX + text],
        normalize_embeddings=True,
        show_progress_bar=False,
    ).astype("float32")


def _maxsim(cli_name: str, q_vec: np.ndarray) -> float:
    """query 與該 CLI 所有 trigger 的最大 cosine similarity"""
    if _trigger_index is None:
        return 0.0
    indices = _trigger_by_cli.get(cli_name, [])
    if not indices:
        return 0.0
    t_vecs = np.zeros((len(indices), _trigger_index.d), dtype="float32")
    for row, gidx in enumerate(indices):
        _trigger_index.reconstruct(gidx, t_vecs[row])
    return float((t_vecs @ q_vec.T).flatten().max())


def _call_kimi(cli_meta: dict, query: str) -> dict:
    try:
        from openai import OpenAI
    except ImportError:
        return {"_error": "openai 套件未安裝，B 路需要 pip install openai"}

    api_key = os.environ.get("KIMI_API_KEY") or os.environ.get("MOONSHOT_API_KEY")
    if not api_key:
        return {"_error": "KIMI_API_KEY 未設定"}

    client = OpenAI(api_key=api_key, base_url="https://api.moonshot.cn/v1")
    schema = cli_meta.get("params_schema") or cli_meta.get("input_schema", {})
    system = (
        f"你是 {cli_meta['name']} CLI 的參數提取器。"
        f"根據用戶意圖，輸出符合以下 JSON Schema 的參數物件（純 JSON，不加說明）：\n"
        f"{json.dumps(schema, ensure_ascii=False)}"
    )
    resp = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": query},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(resp.choices[0].message.content.strip())


def route(query: str) -> dict:
    """
    回傳兩種結果之一：

    正常路由：
        action="route", cli, cli_meta, params, confidence,
        ex_score, source ("A"/"B"), top3, latency_ms

    需要澄清：
        action="clarify", choices=[{name, description, pain_point, score}, ...], latency_ms
    """
    t0 = time.perf_counter()
    _load()

    # ── Stage 1：mean-sim 找 top-3 ────────────────────────────────────────────
    q_vec = _encode_query(query)
    raw_scores, raw_indices = _cli_index.search(q_vec, CLI_TOP_K)
    raw_scores  = raw_scores[0].tolist()
    raw_indices = raw_indices[0].tolist()

    # ── Re-rank：MaxSim 重新排序 top-3 ────────────────────────────────────────
    reranked = []
    for idx, mean_sim in zip(raw_indices, raw_scores):
        if idx < 0:
            continue
        name     = _cli_meta[idx]["name"]
        max_sim  = _maxsim(name, q_vec)
        combined = RERANK_ALPHA * mean_sim + (1 - RERANK_ALPHA) * max_sim
        reranked.append((idx, mean_sim, max_sim, combined))
    reranked.sort(key=lambda x: x[3], reverse=True)

    top3 = [
        {"name": _cli_meta[idx]["name"], "score": round(combined, 4)}
        for idx, _, _, combined in reranked
    ]

    best_idx     = reranked[0][0]
    best_score   = reranked[0][3]
    second_score = reranked[1][3] if len(reranked) > 1 else 0.0
    best_cli_meta = _cli_meta[best_idx]
    cli_name      = best_cli_meta["name"]

    # ── 澄清判斷 ─────────────────────────────────────────────────────────────
    if best_score < CLARIFY_MIN_SCORE and best_score - second_score < CLARIFY_MIN_GAP:
        return {
            "action":     "clarify",
            "choices":    [
                {"name": _cli_meta[idx]["name"], "description": _cli_meta[idx].get("description", "")}
                for idx, *_ in reranked
            ],
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
        }

    # ── Stage 2：example 查表 ─────────────────────────────────────────────────
    ex_entries    = _example_by_cli.get(cli_name, [])
    best_ex_score = 0.0
    best_params   = {}

    if ex_entries:
        ex_indices = [i for i, _ in ex_entries]
        ex_vecs    = np.zeros((len(ex_indices), _example_index.d), dtype="float32")
        for row, gidx in enumerate(ex_indices):
            _example_index.reconstruct(gidx, ex_vecs[row])
        sims          = (ex_vecs @ q_vec.T).flatten()
        best_row      = int(sims.argmax())
        best_ex_score = float(sims[best_row])
        best_params   = ex_entries[best_row][1]["params"]

    # ── A / B 分流 ────────────────────────────────────────────────────────────
    source = "A" if best_ex_score >= EXAMPLE_THRESHOLD else "B"
    if source == "A":
        params = best_params
    else:
        try:
            params = _call_kimi(best_cli_meta, query)
        except Exception:
            params = {}  # B路 API 不可用時降級，CLI routing 結果仍有效

    return {
        "action":     "route",
        "cli":        cli_name,
        "cli_meta":   best_cli_meta,
        "params":     params,
        "confidence": round(best_score, 4),
        "ex_score":   round(best_ex_score, 4),
        "source":     source,
        "top3":       top3,
        "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
    }


# ── CLI 入口 ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python poc/router.py \"你的查詢\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"\n查詢：{query}\n載入中...\n")
    result = route(query)

    if result["action"] == "clarify":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"命中 CLI   : {result['cli']}")
        print(f"描述       : {result['cli_meta'].get('description', '')}")
        print(f"信心分數   : {result['confidence']}")
        print(f"路由路徑   : {result['source']} 路")
        print(f"推斷參數   : {json.dumps(result['params'], ensure_ascii=False)}")
        print(f"延遲       : {result['latency_ms']} ms")
        print(f"\nTop-3：")
        for t in result["top3"]:
            print(f"  {t['score']:.4f}  {t['name']}")
