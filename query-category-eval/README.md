# RAG Query Category Evaluation

Supplementary research for the blog post "Making Legacy Knowledge Searchable with RAG".

## Overview

This evaluation measures RAG system performance across different query categories using Oracle Essbase 11.1.x documentation as the test corpus.

## Methodology

### Four-Phase Evaluation

1. **Phase 1: Light Sampling** (8 queries)
   - Initial exploration across 4 categories
   - Identified failure modes and patterns
   - Applied query expansion fixes

2. **Phase 2: Expanded Sampling** (12 queries)
   - Expanded to n=5 per category (20 total with Phase 1)
   - Systematic scoring with failure mode classification

3. **Phase 3: Ground Truth Validation** (4 queries)
   - Validated high-confidence passes against source corpus
   - Checked for false positives
   - Confirmed 0% false positive rate

4. **Phase 4: Publication Sampling** (20 queries)
   - Expanded to n=10 per category (40 total)
   - Larger sample size for publication confidence
   - Additional ground truth validation

### Scoring Criteria

- **pass**: Complete, accurate answer from retrieved context
- **partial**: Useful information but incomplete or with caveats
- **fail**: Unable to answer or incorrect information

### Failure Modes

- **corpus_gap**: Knowledge does not exist in the corpus (honest "I don't know")
- **scattered_info**: Information exists but spread across multiple sections
- **incomplete**: Partial answer, system admits limitations

## Results Summary

### Success Rates by Category (n=10 each)

| Category | Pass | Partial | Fail | Success Rate | Confidence |
|----------|------|---------|------|--------------|------------|
| Error Lookup | 5 | 1 | 4 | 50-60% | Medium |
| Conceptual | 9 | 1 | 0 | 90-100% | High |
| Procedural | 10 | 0 | 0 | 100% | High |
| Multi-hop | 5 | 2 | 3 | 50-70% | Medium |

### Phase 3-4 Validation Results

- **Queries validated**: 8 (4 in Phase 3, 4 in Phase 4)
- **False positive rate**: 0%
- **Average accuracy**: 97.8%

### Key Findings

1. **Conceptual and procedural queries excel** (90-100%)
   - Clear, well-structured documentation sections
   - Query expansion with domain terms helps retrieval

2. **Error lookup is variable** (50-60%)
   - Specific error codes often not in corpus (corpus gap)
   - General troubleshooting guidance works well
   - Symptom-based queries outperform code-based queries

3. **Multi-hop queries improved with targeted questions** (50-70%)
   - "Best practices" scattered across multiple sections
   - Cross-version features (cloud, REST API) not in 11.x docs
   - Specific optimization questions perform better than generic ones
   - Honest failures are appropriate behavior

## Files

| File | Description |
|------|-------------|
| `phase1_results.json` | Raw results from 8 initial queries |
| `phase2_results.json` | Raw results from 12 expanded queries |
| `phase3_validation.json` | Ground truth validation of 4 Phase 1-2 passes |
| `phase4_results.json` | Raw results from 20 additional queries |
| `phase4_validation.json` | Ground truth validation of 4 Phase 4 passes |
| `PHASE1_SUMMARY.md` | Phase 1 analysis and observations |
| `PHASE2_SUMMARY.md` | Phase 2 analysis with combined statistics |
| `query_classification.json` | Query taxonomy and classification scheme |
| `run_phase1_eval.py` | Script for Phase 1 evaluation |
| `run_phase2_eval.py` | Script for Phase 2 evaluation |
| `run_phase4_eval.py` | Script for Phase 4 evaluation |

## Blog Table (Final)

Based on 40 queries with ground truth validation:

| Query Category | Success Rate | Common Failure Mode | Mitigation |
|----------------|--------------|---------------------|------------|
| Error lookup | 50-60% | Exact code not in corpus | Hybrid retrieval (BM25 + vector) |
| Conceptual | 90-100% | (rare failures) | Query expansion with domain terms |
| Procedural | 100% | (rare failures) | Query expansion with command names |
| Multi-hop | 50-70% | Knowledge scattered or missing | Corpus expansion; honest "not found" |

## Corpus

- **Source**: Oracle Essbase 11.1.x documentation
- **Size**: 7,432 pages, 20,679 chunks
- **Versions**: 11.1.1, 11.1.2.4

## Citation

```
Clouatre, H. (2026). Making Legacy Knowledge Searchable with RAG.
Retrieved from https://clouatre.ca/posts/rag-legacy-knowledge/
```

---

**Last Updated**: 2026-01-24
