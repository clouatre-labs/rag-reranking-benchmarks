#!/usr/bin/env python3
"""
Benchmark RAG retrieval performance with and without reranking.

This is a TEMPLATE script. Adapt for your own RAG implementation by:
1. Replacing imports with your RAG components
2. Defining domain-specific test queries
3. Adjusting retrieval configuration

Measures ONLY retrieval time (not LLM generation) to isolate reranking overhead.

Usage:
    python benchmark_retrieval.py [num_queries]

Requirements:
    - Python 3.11+
    - rich (for console output)
    - Your RAG components (vector store, BM25, reranker)

Example output:
    Reranking Overhead: +31.3ms (+65.5%)
    Note: This is 0.3% of total query time when including LLM generation (~9s)
"""

import json
import sys
import time
from pathlib import Path

# Optional: rich for prettier output (pip install rich)
try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
except ImportError:
    # Fallback to basic print
    class Console:
        def print(self, msg, **kwargs):
            # Strip rich markup for basic output
            import re
            clean = re.sub(r'\[.*?\]', '', str(msg))
            print(clean)
    console = Console()
    Table = None

# =============================================================================
# CUSTOMIZE THIS SECTION FOR YOUR RAG SYSTEM
# =============================================================================

# Replace with your RAG imports
# from your_rag import (
#     HybridRetriever,
#     create_vector_store,
#     get_embeddings,
#     load_cached_chunks,
#     load_cached_bm25,
# )

# Define test queries for YOUR domain
# These should cover diverse topics in your documentation
TEST_QUERIES = [
    # Configuration queries
    "How do I configure the main settings file?",
    "What ports does the application use?",
    "What are the recommended memory settings?",
    
    # Troubleshooting queries
    "How do I troubleshoot slow performance?",
    "What does error code 1001 mean?",
    "How do I fix connection timeout errors?",
    
    # Architecture queries
    "What is the system architecture?",
    "How does the application handle concurrent users?",
    "What are the different storage options?",
    
    # Integration queries
    "How do I integrate with external systems?",
    "What are the API capabilities?",
    "How do I automate common tasks?",
    
    # Best practices
    "What are the security best practices?",
    "How do I optimize performance?",
    "What are the backup procedures?",
    
    # Scripting/automation
    "How do I write automation scripts?",
    "What scripting languages are supported?",
    "How do I schedule batch jobs?",
    
    # Monitoring
    "How do I monitor system health?",
    "What metrics should I track?",
]

# Retrieval configuration
RERANK_TOP_N = 8  # Final number of results after reranking
RETRIEVAL_K = 16  # Number of candidates before reranking

# =============================================================================
# BENCHMARK IMPLEMENTATION (modify as needed)
# =============================================================================


def setup_rag_components():
    """
    Initialize RAG components once (with caching).
    
    CUSTOMIZE: Replace with your RAG initialization code.
    """
    console.print("\n[bold yellow]Setting up RAG components...[/bold yellow]")
    
    # Example implementation (replace with your code):
    # embeddings = get_embeddings()
    # chunks = load_cached_chunks()
    # vector_store = create_vector_store(chunks, embeddings, use_cache=True)
    # bm25 = load_cached_bm25()
    
    # Placeholder - replace with your actual components
    raise NotImplementedError(
        "Replace setup_rag_components() with your RAG initialization code"
    )
    
    # return chunks, vector_store, bm25


def create_retriever(chunks, vector_store, bm25, use_rerank: bool):
    """
    Create a retriever with or without reranking.
    
    CUSTOMIZE: Replace with your retriever construction.
    """
    # Example implementation:
    # return HybridRetriever(
    #     chunks, 
    #     vector_store, 
    #     k=RERANK_TOP_N if use_rerank else RETRIEVAL_K,
    #     bm25=bm25, 
    #     use_rerank=use_rerank
    # )
    
    raise NotImplementedError(
        "Replace create_retriever() with your retriever construction code"
    )


def retrieve(retriever, query: str):
    """
    Execute retrieval for a query.
    
    CUSTOMIZE: Replace with your retrieval call.
    """
    # Example: return retriever.invoke(query)
    raise NotImplementedError(
        "Replace retrieve() with your retrieval call"
    )


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


def run_benchmark(num_queries: int = 20, num_runs: int = 3):
    """Run retrieval benchmark comparing with/without reranking."""
    console.print(
        f"\n[bold]Benchmarking retrieval: {num_queries} queries, "
        f"{num_runs} runs each...[/bold]\n"
    )
    
    # Setup components once
    chunks, vector_store, bm25 = setup_rag_components()
    
    # Select queries
    queries = TEST_QUERIES[:num_queries]
    
    results_with = []
    results_without = []
    
    for i, query in enumerate(queries, 1):
        console.print(f"\n[bold cyan]Query {i}/{num_queries}:[/bold cyan] {query[:50]}...")
        
        # Benchmark with reranking
        result_with = benchmark_retrieval(
            query, chunks, vector_store, bm25, use_rerank=True, num_runs=num_runs
        )
        results_with.append(result_with)
        console.print(f"  [green]With reranking: {result_with['avg_latency_ms']}ms[/green]")
        
        # Benchmark without reranking
        result_without = benchmark_retrieval(
            query, chunks, vector_store, bm25, use_rerank=False, num_runs=num_runs
        )
        results_without.append(result_without)
        console.print(f"  [yellow]Without reranking: {result_without['avg_latency_ms']}ms[/yellow]")
        
        # Show difference
        diff = result_with['avg_latency_ms'] - result_without['avg_latency_ms']
        console.print(f"  [dim]Overhead: {diff:+.1f}ms[/dim]")
    
    return results_with, results_without


def calculate_stats(results: list[dict]) -> dict:
    """Calculate aggregate statistics."""
    latencies = [r["avg_latency_ms"] for r in results]
    
    return {
        "count": len(latencies),
        "mean_latency_ms": round(sum(latencies) / len(latencies), 1),
        "min_latency_ms": round(min(latencies), 1),
        "max_latency_ms": round(max(latencies), 1),
        "median_latency_ms": round(sorted(latencies)[len(latencies) // 2], 1),
    }


def display_results(results_with: list[dict], results_without: list[dict]):
    """Display benchmark results."""
    stats_with = calculate_stats(results_with)
    stats_without = calculate_stats(results_without)
    
    console.print("\n\n[bold]Retrieval Benchmark Results[/bold]\n")
    
    if Table:
        # Rich table output
        table = Table(title="Retrieval Performance Comparison")
        table.add_column("Metric", style="cyan")
        table.add_column("With Reranking", style="green")
        table.add_column("Without Reranking", style="yellow")
        table.add_column("Difference", style="magenta")
        
        for metric in ["mean", "median", "min", "max"]:
            key = f"{metric}_latency_ms"
            diff = stats_with[key] - stats_without[key]
            table.add_row(
                f"{metric.title()} Latency",
                f"{stats_with[key]}ms",
                f"{stats_without[key]}ms",
                f"{diff:+.1f}ms",
            )
        
        console.print(table)
    else:
        # Basic output
        console.print("With Reranking:")
        console.print(f"  Mean: {stats_with['mean_latency_ms']}ms")
        console.print(f"  Median: {stats_with['median_latency_ms']}ms")
        console.print("\nWithout Reranking:")
        console.print(f"  Mean: {stats_without['mean_latency_ms']}ms")
        console.print(f"  Median: {stats_without['median_latency_ms']}ms")
    
    # Calculate overhead
    overhead_ms = stats_with['mean_latency_ms'] - stats_without['mean_latency_ms']
    overhead_pct = (overhead_ms / stats_without['mean_latency_ms']) * 100
    
    console.print(f"\n[bold]Reranking Overhead:[/bold]")
    console.print(f"  {overhead_ms:+.1f}ms ({overhead_pct:+.1f}%)")
    console.print(f"\n[dim]Note: Measures retrieval only, not LLM generation[/dim]")


def save_results(results_with: list[dict], results_without: list[dict], output_file: Path):
    """Save summary results to JSON (no query text for privacy)."""
    data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "num_queries": len(results_with),
        "measurement": "retrieval_only",
        "with_reranking": calculate_stats(results_with),
        "without_reranking": calculate_stats(results_without),
        "overhead_ms": round(
            calculate_stats(results_with)["mean_latency_ms"] - 
            calculate_stats(results_without)["mean_latency_ms"], 
            1
        ),
    }
    
    output_file.write_text(json.dumps(data, indent=2))
    console.print(f"\n[green]Results saved to {output_file}[/green]")


def main():
    """Run the benchmark."""
    num_queries = 20
    if len(sys.argv) > 1:
        try:
            num_queries = int(sys.argv[1])
        except ValueError:
            console.print("[red]Usage: benchmark_retrieval.py [num_queries][/red]")
            sys.exit(1)
    
    # Run benchmark
    results_with, results_without = run_benchmark(num_queries, num_runs=3)
    
    # Display results
    display_results(results_with, results_without)
    
    # Save to file
    output_file = Path("results_summary.json")
    save_results(results_with, results_without, output_file)
    
    console.print("\n[bold green]Benchmark complete![/bold green]")


if __name__ == "__main__":
    main()
