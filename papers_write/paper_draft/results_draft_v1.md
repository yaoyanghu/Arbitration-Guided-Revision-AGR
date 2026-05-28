# Results Draft V1

## Main Retrieval Result

Table 1 reports the main independent validation result on the disjoint 1000 official FEVER split. Relative to BM25, the title-overlap variant improves strict Recall@1 from 0.368 to 0.415 and strict Recall@5 from 0.627 to 0.680, while strict Recall@10 remains unchanged at 0.720. The same pattern appears under relaxed evaluation, though the gains are smaller. This result supports a narrow but important conclusion: lightweight title-aware lexical reranking can improve early-rank evidence-page ordering over a fixed BM25 candidate pool.

The unchanged Recall@10 is especially important for interpretation. It indicates that the gain does not come from expanding candidate coverage or retrieving previously missing evidence pages. Instead, the benefit comes from reordering already retrieved candidates so that the gold evidence page more often appears near the top of the list. In other words, the method improves ranking quality rather than retrieval breadth.

## Label-Wise Results

The label-wise strict results show that the improvement is not confined to a single claim type. For SUPPORTS, strict Recall@1 increases from 0.411 to 0.466 and strict Recall@5 increases from 0.696 to 0.732. For REFUTES, strict Recall@1 increases from 0.325 to 0.365 and strict Recall@5 increases from 0.560 to 0.629. Strict Recall@10 remains unchanged for both labels. These results suggest that the reranking effect is not limited to only positive or only negative evidence matching, but instead improves early-rank ordering across both major FEVER label groups.

## Statistical Support

The BM25 versus title-overlap comparison is also statistically supported. The strict top1 paired comparison yields discordant pairs of 49 versus 2, corresponding to an exact McNemar-style two-sided p-value of 1.17861e-12. Bootstrap confidence intervals for the BM25-to-title-overlap deltas are positive for all reported Recall@1 and Recall@5 metrics. Under strict evaluation, the Recall@1 delta is 0.047 with a 95% confidence interval of [0.034, 0.061], and the Recall@5 delta is 0.053 with a 95% confidence interval of [0.039, 0.068]. These statistics justify presenting the BM25 versus title-overlap comparison as a stable main result rather than a one-off descriptive fluctuation.

## Nearest Title-Aware Baseline Comparison

The broader method interpretation changes when we compare title overlap with the nearest simpler title-aware lexical baseline. On the same disjoint 1000 split, exact title boost achieves strict Recall@1 / Recall@5 / Recall@10 of 0.544 / 0.708 / 0.720, compared with 0.415 / 0.680 / 0.720 for title overlap. Thus, exact title boost is stronger in absolute retrieval gain among the currently tested lightweight title-aware heuristics.

This comparison does not invalidate the BM25 versus title-overlap result. Instead, it changes the level of the paper's claim. The paper can still argue that title overlap is effective relative to BM25 and statistically supported under strict evaluation. What it should no longer argue is that title overlap is itself the strongest lightweight title-aware method. A more accurate reading of the current evidence is that title-aware lexical reranking is effective as a family, with exact title boost acting as the stronger nearby baseline and title overlap behaving as a more conservative alternative with fewer regressions.

## Overall Interpretation

Taken together, the results support a retrieval-only conclusion. Lightweight title-aware lexical reranking improves strict early-rank evidence-page ordering on official FEVER without changing candidate-set coverage at Recall@10. The title-overlap variant remains a valid and statistically supported main comparison against BM25, while the nearest-baseline comparison clarifies that exact title boost is stronger among the tested lightweight heuristics. This is therefore a paper about retrieval-stage reranking quality, not about complete FEVER verification and not about a complete ChronoRAG system.
