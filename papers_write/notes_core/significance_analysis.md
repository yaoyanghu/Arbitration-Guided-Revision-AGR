# Significance Analysis

## Setup

- dataset: official FEVER evidence retrieval
- split: disjoint 1000
- baseline: BM25 candidate retrieval
- improved: BM25 + title overlap reranking with `bm25_weight=0.5`, `title_weight=0.5`
- statistics source: existing `retrieval_results.jsonl`, `predictions.jsonl`, and the current strict evaluation definition

## Paired Significance for Strict Top1

- Discordant pairs: baseline wrong / improved correct = `49`, baseline correct / improved wrong = `2`
- Exact McNemar-style two-sided p-value = `1.17861e-12`
- Conclusion: the strict top1 improvement is **statistically significant** under a paired test.

## Bootstrap Confidence Intervals

Strict metrics:
- BM25 strict Recall@1: 0.368 [0.338, 0.398]
- BM25 + title overlap strict Recall@1: 0.415 [0.385, 0.446]
- Strict Recall@1 delta: 0.047 [0.034, 0.061]
- BM25 strict Recall@5: 0.627 [0.597, 0.657]
- BM25 + title overlap strict Recall@5: 0.680 [0.652, 0.708]
- Strict Recall@5 delta: 0.053 [0.039, 0.068]

Relaxed supplementary metrics:
- BM25 relaxed Recall@1: 0.737 [0.710, 0.763]
- BM25 + title overlap relaxed Recall@1: 0.760 [0.734, 0.786]
- Relaxed Recall@1 delta: 0.023 [0.012, 0.035]
- BM25 relaxed Recall@5: 0.883 [0.863, 0.903]
- BM25 + title overlap relaxed Recall@5: 0.895 [0.876, 0.914]
- Relaxed Recall@5 delta: 0.012 [0.004, 0.021]

## Paper Wording Suggestion

A concise paper-safe wording is:

> On the disjoint 1000 official FEVER validation split, title-overlap reranking improved strict Recall@1 from 0.368 to 0.415 and strict Recall@5 from 0.627 to 0.680. A paired exact McNemar-style test on strict top1 correctness indicated that this gain was statistically significant (p=1.18e-12). Bootstrap confidence intervals likewise showed a positive strict Recall@1 delta of 0.047 [0.034, 0.061] and a positive strict Recall@5 delta of 0.053 [0.039, 0.068].

## Scope Note

- These statistics quantify ranking improvement under the current strict FEVER gold-page matching definition.
- They do not change the qualitative interpretation that Recall@10 is unchanged and the gain comes from reranking within a fixed candidate pool.