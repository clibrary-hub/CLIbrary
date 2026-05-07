# CLIbrary

> Production-grade tool routing for AI agents.

[![PyPI](https://img.shields.io/pypi/v/clibrary-hub.svg)](https://pypi.org/project/clibrary-hub/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)

---

## The Problem

AI agents waste massive amounts of tokens on tool selection. When an agent has 100+ available tools, current approaches force LLMs to read every tool's documentation in the context window before making a decision:

- **Token waste**: 50,000+ tokens per call just for tool descriptions
- **High latency**: 2–5 seconds before any actual work happens
- **Poor accuracy**: LLMs get "lost in the middle" with too many options
- **Unbounded cost**: Linear cost growth as tool count increases

When you scale beyond 50 tools, current systems break down.

---

## How CLIbrary Works

CLIbrary uses a two-stage retrieval architecture to route agent intents to the right tool in ~36ms using only ~150 tokens.

```
Traditional approach:
  Agent intent → Stuff all 500 tools into LLM → LLM picks
  ~50,000 tokens, ~3 seconds, ~70% accuracy

CLIbrary approach:
  Agent intent → CLIbrary router → Single tool + params
  ~150 tokens, ~36ms, ~93% top-3 accuracy
```

### Architecture

```
Agent intent
    │
    ▼
Embed (multilingual-e5-base, ~10ms)
    │
    ▼
Stage 1: FAISS cli_index → top-3 candidates (~5ms)
    │
    ▼
MaxSim re-rank  (combined = 0.7×mean_sim + 0.3×max_sim)
    │
    ├── low confidence + small gap → Clarify (return top-3 to LLM)
    │
    └── high confidence
            │
            ▼
        Stage 2: example_index → best matching example
            │
            ├── sim ≥ 0.85 → Path A: template fill (no LLM, ~80% of calls)
            │
            └── sim < 0.85 → Path B: LLM param extraction (~20% of calls)
                    │
                    ▼
              Tool call JSON output
```

---

## Quick Start

### Install

```bash
pip install clibrary-hub
```

### Build the FAISS indices from your manifests

```bash
clibrary-build-index --manifest-dir ./manifests
# Indices written to ~/.clibrary/indices by default
```

### Route an intent

```python
from clibrary_hub import CLIbrary

router = CLIbrary()
result = router.route("幫我查上週銷售總額")

# {
#   "action": "route",
#   "cli": "sql-runner",
#   "params": {"query": "SELECT SUM(amount) FROM orders WHERE ...", "output_format": "json"},
#   "confidence": 0.94,
#   "source": "A",
#   "latency_ms": 36
# }
```

---

## Performance

Evaluated on 2,050 queries across 500 CLIs:

| Metric | Result |
|--------|--------|
| Top-1 accuracy | 82.3% |
| Top-3 accuracy | 92.5% |
| Path A hit rate (no LLM needed) | 93.6% |
| Median latency | 36ms |
| Token usage | ~150 |

Compared to traditional "stuff all tools into LLM" approach:

| Metric | CLIbrary | Traditional |
|--------|----------|-------------|
| Tokens | ~150 | ~50,000 |
| Latency | 36ms | 2–5s |
| Accuracy (100+ tools) | 82–92% | 60–75% |

---

## Manifest Format

Each CLI tool has a `manifest.json` describing its purpose, inputs, and examples:

```json
{
  "name": "sql-runner",
  "version": "1.0.0",
  "category": "data",
  "description": "Execute SQL queries against a database",
  "intent_triggers": [
    "query a database",
    "run a SQL statement",
    "查資料庫",
    "跑 SQL"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {"type": "string", "description": "SQL query to execute"},
      "output_format": {"type": "string", "enum": ["json", "csv", "table"], "default": "json"}
    },
    "required": ["query"]
  },
  "examples": [
    {
      "query": "查上週銷售總額",
      "params": {"query": "SELECT SUM(amount) FROM orders WHERE created_at > NOW() - INTERVAL 7 DAY", "output_format": "json"}
    }
  ],
  "tags": ["sql", "database", "query"]
}
```

---

## Three FAISS Indices

| Index | Vectors | Content | Usage |
|-------|---------|---------|-------|
| `cli_index` | 500 | Mean-pooled intent_triggers per CLI | Stage 1 candidate retrieval |
| `trigger_index` | ~3,500 | Individual trigger vectors | MaxSim re-ranking |
| `example_index` | ~1,500 | Example query vectors | Stage 2 template matching |

---

## Project Structure

```
CLIbrary/
├── src/clibrary_hub/
│   ├── __init__.py
│   ├── router.py          # Core routing logic
│   ├── build_index.py     # FAISS index builder (clibrary-build-index)
│   ├── manifest.py        # Manifest loader / validator
│   ├── matchers/
│   └── utils/
├── benchmark/
│   └── eval_sets/         # in_domain / paraphrase / cross_domain (2,050 queries)
├── tests/
└── README.md
```

---

## Why It Works

1. **Embedding routing beats LLM selection** at scale — geometric distance is not affected by "lost in the middle" attention dilution.
2. **Two-stage design** improves accuracy: broad candidate retrieval in Stage 1, precise example matching in Stage 2.
3. **Example-based caching** eliminates LLM calls for ~80% of queries.
4. **Multilingual** (multilingual-e5-base) handles mixed Chinese/English queries natively.

---

## Comparison

| | CLIbrary | LangChain Tool Retrieval | Function Calling | MCP |
|-|----------|--------------------------|-----------------|-----|
| Scales to 500+ tools | ✅ | ⚠️ | ❌ | ⚠️ |
| No LLM for routing | ✅ (80%) | ❌ | ❌ | ❌ |
| Manifest standard | ✅ | ❌ | ❌ | ✅ |
| Multilingual | ✅ | ⚠️ | ⚠️ | ⚠️ |

CLIbrary complements MCP: CLIbrary handles routing, MCP handles protocol.

---

## Status

- ✅ Manifest schema v1.0
- ✅ 500 CLI manifests (8 categories)
- ✅ Reference router implementation (FAISS, multilingual-e5-base)
- ✅ Evaluation dataset (2,050 queries)
- ✅ pip package — `pip install clibrary-hub`

---

## License

MIT License — free to use, including for commercial purposes.

---

## Links

- PyPI: https://pypi.org/project/clibrary-hub/
- GitHub: https://github.com/clibrary-hub/CLIbrary
- Manifest registry: https://github.com/clibrary-hub/manifests
