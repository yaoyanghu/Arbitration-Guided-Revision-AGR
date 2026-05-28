# FEVER Short Paper Draft Outline

## Abstract

- Introduce the paper as a retrieval-only study on official FEVER evidence retrieval.
- State the task family as lightweight title-aware lexical reranking over a fixed BM25 candidate pool.
- Identify the main independent evaluation anchor as the disjoint 1000-query validation split.
- Report the core BM25 vs title-overlap result under strict evaluation.
- Clarify that Recall@10 remains unchanged, so the gain comes from reranking rather than coverage expansion.
- Note that exact title boost is a stronger tested nearby baseline, which narrows the paper's claim to the broader title-aware lexical reranking family.

## 1. Introduction

- Motivate evidence retrieval quality as a bottleneck for fact verification pipelines.
- Narrow the scope: this paper studies retrieval-stage reranking, not end-to-end FEVER verification and not full ChronoRAG.
- Explain why strict gold-page ranking matters more than only loose top-k retrieval success.
- Introduce the central question: can lightweight title-aware lexical signals improve early-rank evidence ordering over BM25?
- Present the main finding: title-overlap reranking improves strict early-rank retrieval on a disjoint 1000 split.
- Immediately qualify the finding: among tested lightweight title-aware lexical heuristics, exact title boost is stronger, so the paper's claim should stay at the title-aware lexical reranking level.
- Summarize contributions in a restrained way: main result, strict-vs-relaxed evaluation, label-wise and significance analysis, nearest-baseline comparison.

## 2. Method

- Define the retrieval setting: BM25 retrieves a fixed candidate pool, then lightweight title-aware lexical reranking reorders candidates.
- Describe the BM25 baseline at a high level.
- Describe the title-overlap variant as a token-level title-aware lexical reranker.
- Describe the exact-title-boost variant as the nearest simpler title-aware heuristic used for comparison.
- Explain why the paper keeps BM25 vs title overlap as the main validation line: it is the historically developed variant with full significance and case-analysis support.
- Clarify that the method family studied here is title-aware lexical reranking, not a complete verification model and not a ChronoRAG system.

## 3. Experimental Setup

- State the dataset as official FEVER.
- Define the main split as the disjoint 1000-query validation set.
- Explain that this split is used as the main anchor because earlier validation overlap issues were repaired.
- Describe strict evaluation: gold page must exactly match official evidence titles after normalization.
- Describe relaxed evaluation as supplementary and clearly secondary.
- Note that the main reported comparisons are BM25 vs title overlap, with exact title boost shown as the nearest-baseline comparison.
- Mention label-wise analysis for SUPPORTS and REFUTES.
- Mention paired significance and bootstrap confidence intervals for BM25 vs title overlap.

## 4. Results

- Start with the main disjoint 1000 result table.
- Emphasize strict Recall@1 and Recall@5 improvement for title overlap over BM25.
- Emphasize unchanged Recall@10 to support the reranking-not-coverage interpretation.
- Report label-wise strict gains for both SUPPORTS and REFUTES.
- Report significance and CI to show the BM25 vs title-overlap result is statistically supported.
- Then introduce the nearest-baseline comparison table.
- State clearly that exact title boost is stronger than title overlap among tested lightweight title-aware lexical heuristics.
- Reconcile the two findings: title overlap is valid and conservative; exact title boost is stronger in absolute gain.

## 5. Limitations

- Clarify that the paper studies retrieval-only evidence reranking, not full FEVER verification.
- Clarify that the main independent result is on disjoint 1000 rather than completed full-dev confirmation.
- State that title overlap is not the strongest tested title-aware heuristic in the current repository.
- Note that the paper's conclusions apply to early-rank lexical reranking within a fixed candidate pool.
- Mention that runtime discussion is qualitative only in the current draft.

## 6. Conclusion

- Restate the paper's narrow claim: lightweight title-aware lexical reranking helps official FEVER evidence retrieval under strict gold-page evaluation.
- Restate the core empirical finding for BM25 vs title overlap.
- Restate the crucial qualification that exact title boost is stronger among tested nearby heuristics.
- Close by positioning full-dev confirmation and broader ChronoRAG routes as future work rather than prerequisites for the present paper.
