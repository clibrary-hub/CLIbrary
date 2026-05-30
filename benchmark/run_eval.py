"""
Benchmark: compare two router configs on a shared eval subset.

Usage:
    python benchmark/run_eval.py \
        --baseline-dir ~/.clibrary/indices_e5_small \
        --candidate-dir ~/.clibrary/indices_qwen_small \
        --baseline-model intfloat/multilingual-e5-base \
        --candidate-model Qwen/Qwen3-Embedding-0.6B \
        --eval-dir benchmark/eval_sets
"""
import argparse, json, time
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from clibrary_hub.router import CLIbrary


def load_eval(eval_dir: Path, allowed_clis: set[str] | None = None) -> list[dict]:
    rows = []
    for f in sorted(eval_dir.glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if allowed_clis is None or row["expected_cli"] in allowed_clis:
                rows.append(row)
    return rows


def evaluate(router: CLIbrary, rows: list[dict]) -> dict:
    top1 = top3 = path_a = 0
    latencies = []
    for row in rows:
        result = router.route(row["intent"])
        latencies.append(result.get("latency_ms", 0))
        if result["action"] == "route":
            top3_names = [c["name"] for c in result.get("top3", [])]
            if result["cli"] == row["expected_cli"]:
                top1 += 1
            if row["expected_cli"] in top3_names:
                top3 += 1
            if result.get("source") == "A":
                path_a += 1
    n = len(rows)
    latencies.sort()
    return {
        "n": n,
        "top1_acc": round(top1 / n * 100, 1),
        "top3_acc": round(top3 / n * 100, 1),
        "path_a_rate": round(path_a / n * 100, 1),
        "median_ms": round(latencies[n // 2], 1),
        "p95_ms": round(latencies[int(n * 0.95)], 1),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--baseline-dir", required=True, type=Path)
    p.add_argument("--candidate-dir", required=True, type=Path)
    p.add_argument("--baseline-model", default="intfloat/multilingual-e5-base")
    p.add_argument("--candidate-model", default="Qwen/Qwen3-Embedding-0.6B")
    p.add_argument("--eval-dir", default="benchmark/eval_sets", type=Path)
    args = p.parse_args()

    # Use whichever subset is smaller (both built from same seed so same CLIs)
    subset_file = args.baseline_dir / "subset_clis.json"
    allowed = set(json.loads(subset_file.read_text())) if subset_file.exists() else None
    if allowed:
        print(f"Filtering eval to {len(allowed)} CLIs in subset index")

    rows = load_eval(args.eval_dir, allowed)
    print(f"Eval queries: {len(rows)}\n")

    print(f"[BASELINE] {args.baseline_model}")
    baseline = CLIbrary(index_dir=args.baseline_dir, model_name=args.baseline_model)
    b = evaluate(baseline, rows)
    print(f"  Top-1={b['top1_acc']}%  Top-3={b['top3_acc']}%  PathA={b['path_a_rate']}%  Med={b['median_ms']}ms  P95={b['p95_ms']}ms\n")

    print(f"[CANDIDATE] {args.candidate_model}")
    candidate = CLIbrary(index_dir=args.candidate_dir, model_name=args.candidate_model)
    c = evaluate(candidate, rows)
    print(f"  Top-1={c['top1_acc']}%  Top-3={c['top3_acc']}%  PathA={c['path_a_rate']}%  Med={c['median_ms']}ms  P95={c['p95_ms']}ms\n")

    print("=" * 65)
    print(f"{'Metric':<25} {'e5-base (768d)':>16} {'Qwen3-0.6B':>14} {'Delta':>8}")
    print("-" * 65)
    for key, label in [
        ("top1_acc",   "Top-1 Acc (%)"),
        ("top3_acc",   "Top-3 Acc (%)"),
        ("path_a_rate","Path-A Rate (%)"),
        ("median_ms",  "Median Lat (ms)"),
        ("p95_ms",     "P95 Lat (ms)"),
    ]:
        d = c[key] - b[key]
        sign = "+" if d >= 0 else ""
        print(f"  {label:<23} {b[key]:>16} {c[key]:>14} {sign+str(round(d,1)):>8}")
    print("=" * 65)

    out = {"n_queries": len(rows), "baseline": b, "candidate": c,
           "models": {"baseline": args.baseline_model, "candidate": args.candidate_model}}
    Path("benchmark/results.json").write_text(json.dumps(out, indent=2))
    print("\nSaved → benchmark/results.json")

if __name__ == "__main__":
    main()
