# RAG Query Category Evaluation

Supplementary research for the blog post "Making Legacy Knowledge Searchable with RAG".

## Overview

This evaluation measures RAG system performance across different query categories using Oracle Essbase 11.1.x documentation as the test corpus. We conducted a 4-phase evaluation with 32 scored queries and 8 ground truth validations to establish confidence in accuracy metrics.

## Four-Phase Evaluation Approach

### Phase 1: Classification and Light Sampling (8 queries, unscored)

Initial exploration phase to understand query patterns and system behavior:
- 2 queries per category (error_lookup, conceptual, procedural, multi_hop)
- Identified failure modes and retrieval patterns
- Applied query expansion fixes
- Unscored; used for exploration and hypothesis generation

### Phase 2: Initial Evaluation (12 queries, scored)

Systematic evaluation with manual scoring:
- 3 queries per category
- Scoring: pass, partial, fail
- Failure mode classification (corpus_gap, scattered_info, incomplete)
- Results: 7 pass, 3 partial, 2 fail across 12 queries

**Phase 2 Results:**
| Category | Pass | Partial | Fail | Total |
|----------|------|---------|------|-------|
| error_lookup | 1 | 1 | 1 | 3 |
| conceptual | 3 | 0 | 0 | 3 |
| procedural | 3 | 0 | 0 | 3 |
| multi_hop | 0 | 2 | 1 | 3 |

### Phase 3: Ground Truth Validation (4 validations)

Manual corpus search to validate high-confidence passes from Phase 1-2:
- 4 queries validated (2 conceptual, 2 procedural)
- Verified claims against source documentation
- Checked for false positives
- Results: 4/4 verified, 0% false positive rate, 97.5% average accuracy

**Phase 3 Validation Summary:**
- Query 16 (conceptual): 100% accuracy - Architecture explanation matches documentation verbatim
- Query 5 (conceptual): 95% accuracy - MaxL vs ESSCMD comparison verified, minor platform limitation note
- Query 7 (procedural): 95% accuracy - Calculation script steps verified (minor version difference in chapter number)
- Query 2 (procedural): 100% accuracy - essbase.cfg configuration steps match documentation exactly

### Phase 4: Expanded Evaluation (20 queries, scored)

Larger sample for publication confidence:
- 5 queries per category
- Same scoring methodology as Phase 2
- Results: 17 pass, 1 partial, 2 fail across 20 queries

**Phase 4 Results:**
| Category | Pass | Partial | Fail | Total |
|----------|------|---------|------|-------|
| error_lookup | 3 | 0 | 2 | 5 |
| conceptual | 4 | 1 | 0 | 5 |
| procedural | 5 | 0 | 0 | 5 |
| multi_hop | 5 | 0 | 0 | 5 |

### Phase 4 Validation (4 additional validations)

Ground truth validation of Phase 4 high-confidence passes:
- 4 queries validated (1 conceptual, 1 procedural, 1 multi_hop, 1 conceptual)
- Results: 4/4 verified, 0% false positive rate, 98.75% average accuracy

**Phase 4 Validation Summary:**
- Query 46 (conceptual): 100% accuracy - Substitution variables explanation verified
- Query 47 (conceptual): 100% accuracy - Transparent partitioning mechanics verified
- Query 53 (procedural): 100% accuracy - Data export syntax verified
- Query 57 (multi_hop): 95% accuracy - Data load optimization verified (general advice not corpus-specific)

## Combined Results (32 Scored Queries)

Combining Phase 2 (12 queries) and Phase 4 (20 queries):

| Category | Queries | Pass | Partial | Fail | Pass Rate |
|----------|---------|------|---------|------|-----------|
| error_lookup | 8 | 4 | 1 | 3 | 50% |
| conceptual | 8 | 7 | 1 | 0 | 88% |
| procedural | 8 | 8 | 0 | 0 | 100% |
| multi_hop | 8 | 5 | 2 | 1 | 62% |
| **Total** | **32** | **24** | **4** | **4** | **75%** |

## Failure Mode Analysis

### corpus_gap (Missing Documentation)

Occurs when knowledge does not exist in the corpus. This is honest system behavior, not a failure.

**Examples:**
- Specific error codes not documented (e.g., error 1003001)
- Cloud migration features not in on-premise 11.x documentation
- Cross-version features (REST API, cloud-native) absent from legacy docs

**Mitigation:** Expand corpus to newer versions or external sources.

### scattered_info (Information Spread Across Documents)

Knowledge exists but is distributed across multiple sections, making synthesis difficult.

**Examples:**
- "Best practices" for calc script performance mentioned in multiple chapters
- Security best practices scattered across administration and configuration guides
- Multi-hop reasoning requires connecting concepts from different documents

**Mitigation:** Improve query expansion and multi-document synthesis in RAG pipeline.

## Ground Truth Validation Summary

**8 Total Validations (Phase 3 + Phase 4):**
- Phase 3: 4 validations, 97.5% average accuracy
- Phase 4: 4 validations, 98.75% average accuracy
- **Combined: 98.1% average accuracy, 0% false positive rate**

Validation method: Manual corpus search using `rg` (ripgrep) against Oracle Essbase 11.1.x documentation. Each validated query's key claims were cross-referenced against source sections.

## Scoring Criteria

- **pass**: Complete, accurate answer directly supported by retrieved context
- **partial**: Useful information but incomplete, with caveats, or requiring external knowledge
- **fail**: Unable to answer, incorrect information, or corpus gap

## Key Findings

1. **Procedural queries excel** (100% pass rate)
   - Step-by-step instructions are well-structured in documentation
   - Query expansion with command names and configuration parameters helps
   - Consistent across all 8 procedural queries

2. **Conceptual queries perform well** (88% pass rate, 7/8)
   - Architecture, design patterns, and definitions are clearly documented
   - Query expansion with domain terminology improves retrieval
   - 1 partial failure due to scattered information across sections

3. **Error lookup is variable** (50% pass rate, 4/8)
   - Specific error codes often not in corpus (corpus_gap)
   - General troubleshooting guidance works well
   - Symptom-based queries outperform code-based queries
   - Hybrid retrieval (BM25 + vector) helps but cannot overcome missing documentation

4. **Multi-hop queries require synthesis** (62% pass rate, 5/8)
   - Queries requiring cross-document reasoning are challenging
   - Information scattered across multiple sections (scattered_info)
   - Specific optimization questions perform better than generic "best practices"
   - System appropriately admits limitations when corpus lacks comprehensive coverage

## Files

| File | Description |
|------|-------------|
| `phase1_results.json` | Raw results from 8 initial queries (unscored) |
| `phase2_results.json` | Raw results from 12 scored queries |
| `phase3_validation.json` | Ground truth validation of 4 Phase 1-2 passes |
| `phase4_results.json` | Raw results from 20 scored queries |
| `phase4_validation.json` | Ground truth validation of 4 Phase 4 passes |
| `query_classification.json` | Query taxonomy and classification scheme |

## Corpus

- **Source**: Oracle Essbase 11.1.x documentation
- **Size**: 7,432 pages, 20,679 chunks
- **Versions**: 11.1.1, 11.1.2.4
- **Chunk size**: 1,000 tokens with 200-token overlap

## Citation

```bibtex
@misc{clouatre2026raglocalknowledge,
  author = {Clouatre, Hugues},
  title  = {Making Legacy Knowledge Searchable with RAG},
  year   = {2026},
  note   = {Supplementary evaluation: query-category-eval/},
  url    = {https://clouatre.ca/posts/rag-legacy-knowledge/}
}
```

---

**Last Updated**: 2026-02-17
