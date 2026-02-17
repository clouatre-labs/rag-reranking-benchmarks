#!/usr/bin/env python3
"""Statistical analysis of RAG reranking benchmark data.

Reads raw_timings.csv and calculates:
- ANOVA for cross-model variance
- 95% confidence intervals per model
- Mean overhead with standard error

Expected output (matching METHODOLOGY.md):
- F-statistic: 1.10, p-value: 0.34
- Mean overhead: 27.2ms +/-4.6ms
"""

import csv
from collections import defaultdict
from pathlib import Path

import scipy.stats as stats

DATA_PATH = Path(__file__).parent.parent / "data/raw_timings.csv"


def load_data(path: Path) -> list[dict]:
    """Load CSV data."""
    with open(path) as f:
        reader = csv.DictReader(f)
        return [
            {
                "query_id": row["query_id"],
                "model": row["model"],
                "provider": row["provider"],
                "condition": row["condition"],
                "run": int(row["run"]),
                "latency_ms": float(row["latency_ms"]),
            }
            for row in reader
        ]


def calculate_overhead_per_query(data: list[dict]) -> dict[tuple[str, str], float]:
    """Calculate reranking overhead per query per model.

    Overhead = mean(with_rerank) - mean(without_rerank) for each query.
    """
    # Group by (model, query_id, condition)
    grouped: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in data:
        key = (row["model"], row["query_id"], row["condition"])
        grouped[key].append(row["latency_ms"])

    # Calculate overhead per (model, query_id)
    overheads: dict[tuple[str, str], float] = {}
    models_queries = {(row["model"], row["query_id"]) for row in data}

    for model, query_id in models_queries:
        with_rerank = grouped.get((model, query_id, "with_rerank"), [])
        without_rerank = grouped.get((model, query_id, "without_rerank"), [])

        if with_rerank and without_rerank:
            overhead = sum(with_rerank) / len(with_rerank) - sum(without_rerank) / len(
                without_rerank
            )
            overheads[(model, query_id)] = overhead

    return overheads


def calculate_model_overheads(overheads: dict[tuple[str, str], float]) -> dict[str, list[float]]:
    """Group overheads by model."""
    model_overheads: dict[str, list[float]] = defaultdict(list)
    for (model, _query_id), overhead in overheads.items():
        model_overheads[model].append(overhead)
    return dict(model_overheads)


def calculate_anova(model_overheads: dict[str, list[float]]) -> tuple[float, float]:
    """Calculate one-way ANOVA across models (OpenRouter only for cross-model comparison)."""
    # Filter to OpenRouter models only (exclude Bedrock for cross-model ANOVA)
    openrouter_models = [
        overheads
        for model, overheads in model_overheads.items()
        if model != "claude-haiku-4.5"
    ]

    if len(openrouter_models) < 2:
        return 0.0, 1.0

    f_stat, p_value = stats.f_oneway(*openrouter_models)
    return float(f_stat), float(p_value)


def calculate_confidence_interval(
    values: list[float], confidence: float = 0.95
) -> tuple[float, float, float]:
    """Calculate mean and 95% CI."""
    n = len(values)
    mean = sum(values) / n
    std_err = stats.sem(values)
    ci = stats.t.interval(confidence, n - 1, loc=mean, scale=std_err)
    return mean, ci[0], ci[1]


def main():
    """Run statistical analysis."""
    data = load_data(DATA_PATH)
    print(f"Loaded {len(data)} measurements")

    # Calculate overheads
    overheads = calculate_overhead_per_query(data)
    model_overheads = calculate_model_overheads(overheads)

    print("\n=== Per-Model Statistics ===")
    for model, values in sorted(model_overheads.items()):
        mean, ci_low, ci_high = calculate_confidence_interval(values)
        print(f"{model}: {mean:.1f}ms [95% CI: {ci_low:.1f}, {ci_high:.1f}] (n={len(values)})")

    # Calculate overall mean for OpenRouter models
    openrouter_overheads = [
        v for model, values in model_overheads.items() if model != "claude-haiku-4.5" for v in values
    ]
    openrouter_mean, openrouter_ci_low, openrouter_ci_high = calculate_confidence_interval(
        openrouter_overheads
    )

    print("\n=== OpenRouter Aggregate ===")
    print(f"Mean overhead: {openrouter_mean:.1f}ms")
    print(f"95% CI: [{openrouter_ci_low:.1f}, {openrouter_ci_high:.1f}]")

    # Calculate standard error for the mean
    openrouter_model_means = [
        sum(values) / len(values)
        for model, values in model_overheads.items()
        if model != "claude-haiku-4.5"
    ]
    if len(openrouter_model_means) > 1:
        model_std = (
            sum((m - sum(openrouter_model_means) / len(openrouter_model_means)) ** 2 for m in openrouter_model_means)
            / (len(openrouter_model_means) - 1)
        ) ** 0.5
        print(f"Cross-model std: +/-{model_std:.1f}ms")

    # ANOVA
    f_stat, p_value = calculate_anova(model_overheads)
    print("\n=== ANOVA (Cross-Model Variance) ===")
    print(f"F-statistic: {f_stat:.2f}")
    print(f"p-value: {p_value:.2f}")

    # Variance decomposition
    openrouter_models_list = [
        (model, values)
        for model, values in model_overheads.items()
        if model != "claude-haiku-4.5"
    ]
    if openrouter_models_list:
        grand_mean = sum(openrouter_overheads) / len(openrouter_overheads)

        # Between-group variance
        between_var = sum(
            len(values) * ((sum(values) / len(values)) - grand_mean) ** 2
            for _model, values in openrouter_models_list
        ) / (len(openrouter_models_list) - 1)

        # Within-group variance
        within_var = sum(
            sum((v - sum(values) / len(values)) ** 2 for v in values)
            for _model, values in openrouter_models_list
        ) / (len(openrouter_overheads) - len(openrouter_models_list))

        print(f"Between-group variance: {between_var:.1f} ms^2")
        print(f"Within-group variance: {within_var:.1f} ms^2")

    print("\n=== Summary ===")
    print(f"Total measurements: {len(data)}")
    print(f"Models: {len(model_overheads)}")
    print(f"Queries per model: {len(overheads) // len(model_overheads)}")


if __name__ == "__main__":
    main()
