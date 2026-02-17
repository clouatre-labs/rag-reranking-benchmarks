<div align="center">

# RAG Reranking Benchmarks

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/clouatre-labs/rag-reranking-benchmarks?style=flat)](https://github.com/clouatre-labs/rag-reranking-benchmarks)
[![Python](https://img.shields.io/badge/python-3.x-blue)](https://python.org)

Does reranking actually slow down RAG queries? We measured it. 480 timing measurements across 4 model families and 2 providers say: **no, +31ms is noise in a multi-second pipeline.**

Supplementary materials for [Making Legacy Knowledge Searchable with RAG](https://clouatre.ca/posts/rag-legacy-systems/).

</div>

## The Question

Reranking improves retrieval quality by reordering candidate chunks before they reach the LLM. But it adds a neural inference step. In a production RAG pipeline serving legacy enterprise documentation, is the latency cost worth it?

**Short answer:** the cost is 31ms on a 10-second pipeline. That is 0.3% overhead, and it is model-agnostic.

```text
Total query time (typical):  ~10,000ms
├── LLM generation:           ~9,800ms  (98%)
├── Vector + BM25 retrieval:     ~120ms  (1.2%)
├── Reranking (FlashRank):        ~31ms  (0.3%)  <-- this is what we measured
└── Other (embedding, RRF):       ~49ms  (0.5%)
```

## Results

### Reranking Latency (Single-Model, Production)

| Metric | With Reranking | Without Reranking | Delta |
|--------|----------------|-------------------|-------|
| Mean | 79.1ms | 47.8ms | **+31.3ms** |
| Median | 82.1ms | 49.9ms | +32.2ms |
| Min | 50.3ms | 32.5ms | +17.8ms |
| Max | 124.6ms | 80.6ms | +44.0ms |

### Cross-Model Validation

| Model | Size | Provider | Reranking Overhead |
|-------|------|----------|-------------------|
| Claude Haiku 4.5 | - | Amazon Bedrock | baseline |
| Mistral Devstral | 22B | OpenRouter | +32.5ms |
| Llama 3.3 | 70B | OpenRouter | +24.1ms |
| Qwen 2.5 Coder | 32B | OpenRouter | +25.1ms |

ANOVA p=0.34: no statistically significant difference across models. Cross-provider delta (Bedrock vs OpenRouter): 4.1ms.

### Query Category Accuracy

| Category | Queries | Top-1 | Top-3 |
|----------|---------|-------|-------|
| Procedural | 5 | 100% | 100% |
| Conceptual | 5 | 80% | 100% |
| Troubleshooting | 5 | 100% | 100% |
| Configuration | 5 | 60% | 80% |
| **Overall** | **20** | **85%** | **95%** |

0% false positive rate. 97.8% average accuracy on ground truth validation. See `query-category-eval/` for phase-by-phase results.

## System Under Test

```text
Corpus:      7,432 pages / 20,679 chunks (Oracle Essbase 11.1.x documentation)
Retrieval:   Hybrid (BM25 + vector search, RRF fusion)
Reranker:    FlashRank ms-marco-MiniLM-L-12-v2 (~4MB, CPU-only)
Pipeline:    16 candidates retrieved, reranked to top 8
Hardware:    MacBook Pro M-series (CPU only, no GPU)
Measurements: 480 total (120 single-model + 360 multi-model)
```

## How It Works

The benchmark template measures retrieval latency with and without reranking, averaging over multiple runs per query:

```python
def benchmark_retrieval(
    query: str,
    chunks,
    vector_store,
    bm25,
    use_rerank: bool = True,
    num_runs: int = 3,
) -> dict:
    """Benchmark retrieval for a single query (average over multiple runs)."""
    retriever = create_retriever(chunks, vector_store, bm25, use_rerank)

    latencies = []
    for _ in range(num_runs):
        start = time.perf_counter()
        docs = retrieve(retriever, query)
        latency_ms = (time.perf_counter() - start) * 1000
        latencies.append(latency_ms)

    avg_latency = sum(latencies) / len(latencies)

    return {
        "mode": "with_rerank" if use_rerank else "without_rerank",
        "avg_latency_ms": round(avg_latency, 1),
        "min_latency_ms": round(min(latencies), 1),
        "max_latency_ms": round(max(latencies), 1),
        "num_docs": len(docs) if docs else 0,
    }
```

The statistical analysis script validates cross-model consistency with one-way ANOVA:

```python
def calculate_overhead_per_query(data: list[dict]) -> dict[tuple[str, str], float]:
    """Calculate reranking overhead per query per model.

    Overhead = mean(with_rerank) - mean(without_rerank) for each query.
    """
    grouped: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in data:
        key = (row["model"], row["query_id"], row["condition"])
        grouped[key].append(row["latency_ms"])

    overheads: dict[tuple[str, str], float] = {}
    models_queries = {(row["model"], row["query_id"]) for row in data}

    for model, query_id in models_queries:
        with_rerank = grouped.get((model, query_id, "with_rerank"), [])
        without_rerank = grouped.get((model, query_id, "without_rerank"), [])

        if with_rerank and without_rerank:
            overhead = (
                sum(with_rerank) / len(with_rerank)
                - sum(without_rerank) / len(without_rerank)
            )
            overheads[(model, query_id)] = overhead

    return overheads
```

## Project Structure

```text
rag-reranking-benchmarks/
├── README.md                          # This file
├── METHODOLOGY.md                     # Measurement approach and statistical methods
├── LICENSE                            # Apache-2.0
├── benchmark_retrieval.py             # Reproducible benchmark template
├── results_summary.json               # Aggregate timing data
├── data/
│   └── raw_timings.csv                # 480 anonymized measurements
├── scripts/
│   └── stats_analysis.py              # ANOVA, 95% CI, cross-model comparison
└── query-category-eval/
    ├── README.md                      # Evaluation methodology
    ├── query_classification.json      # 20 queries across 4 categories
    ├── phase1_initial_results.json    # Raw RAG responses
    ├── phase2_ground_truth.json       # Manual ground truth labels
    ├── phase3_validation_results.json # Automated accuracy scoring
    └── phase4_analysis.json           # Final analysis and failure modes
```

## Reproducing

```bash
git clone https://github.com/clouatre-labs/rag-reranking-benchmarks
cd rag-reranking-benchmarks

# Run statistical analysis on existing data
python scripts/stats_analysis.py

# Adapt the benchmark template for your own RAG system
# (see inline comments in benchmark_retrieval.py)
```

See [METHODOLOGY.md](METHODOLOGY.md) for the full measurement approach.

## Adapting for Your System

The benchmark script is a template. To benchmark your own RAG pipeline:

1. Replace imports with your retrieval and reranking components
2. Define domain-specific test queries
3. Adjust retrieval parameters (k, reranking model, candidate count)

The statistical analysis script works on any CSV with the same column schema as `data/raw_timings.csv`.

## Citation

```bibtex
@misc{clouatre2026ragreranking,
  author = {Clouatre, Hugues},
  title  = {RAG Reranking Benchmarks},
  year   = {2026},
  note   = {Supplementary materials for "Making Legacy Knowledge Searchable with RAG"},
  url    = {https://clouatre.ca/posts/rag-legacy-systems/}
}
```

## License

[Apache-2.0](LICENSE)
