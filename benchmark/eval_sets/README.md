# Evaluation Datasets

This directory contains evaluation datasets used in the CLIbrary routing benchmark.

## Files

| File | Queries | Description |
|------|---------|-------------|
| `in_domain.jsonl` | 500 | Standard queries, canonical phrasing |
| `cross_domain.jsonl` | 50 | Queries that span multiple CLI categories |
| `paraphrase.jsonl` | ~1,500 | Paraphrase variants (colloquial, mixed, vague) |

## Format

Each line is a JSON object:

```json
{
  "intent": "analyze my sales CSV file",
  "expected_cli": "csv-stat",
  "expected_params_keys": ["file"],
  "tag": "in-domain"
}
```

## Benchmark Results

See `poc/eval/results.csv` for full routing results.

Summary (2,050 queries, 500 CLIs):

| Metric | Value |
|--------|-------|
| Top-1 accuracy | 82.3% |
| Top-3 accuracy | 92.5% |
| Path A hit rate | 93.6% |
| Median latency | 36ms |
