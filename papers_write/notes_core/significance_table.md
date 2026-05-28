# Significance Table

Context:
- comparison shown here is `routeA_bm25` vs `routeA_bm25_title_overlap`
- this table supports the title-overlap variant as a statistically valid member of the title-aware lexical reranking family
- it does not claim title overlap is the strongest tested lightweight heuristic

| metric | baseline | title-overlap | delta | 95% CI for delta |
| --- | ---: | ---: | ---: | --- |
| strict Recall@1 | 0.368 | 0.415 | 0.047 | [0.034, 0.061] |
| strict Recall@5 | 0.627 | 0.680 | 0.053 | [0.039, 0.068] |
| relaxed Recall@1 | 0.737 | 0.760 | 0.023 | [0.012, 0.035] |
| relaxed Recall@5 | 0.883 | 0.895 | 0.012 | [0.004, 0.021] |

Caption-style wording:
For the BM25 vs title-overlap comparison on the disjoint 1000 split, the strict top1 paired test uses discordant pairs `49` vs `2`, yielding exact McNemar-style two-sided `p=1.17861e-12`. All reported Recall@1 and Recall@5 deltas have positive bootstrap confidence intervals, confirming that the title-overlap variant is statistically supported relative to BM25.
