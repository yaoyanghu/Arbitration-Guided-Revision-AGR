# Results

This project now has two distinct 1000-query results that must not be conflated.

- The older `fever_official_route_a_1000` result is a larger follow-up evaluation, but it is not an independent validation because it overlaps with the 500-query tuning set.
- The newer `fever_official_route_a_disjoint_1000` result is the correct independent validation split and should be treated as the main paper result.

Under the disjoint 1000 validation split, the lightweight reranking method still improves evidence retrieval quality under strict gold-page matching. With `bm25_weight=0.5` and `title_weight=0.5`, strict Recall@1 improves from `0.368` to `0.415`, and strict Recall@5 improves from `0.627` to `0.680`. Strict Recall@10 remains unchanged at `0.720`, which again indicates that the method improves ranking quality rather than candidate-set coverage.

The relaxed metrics show the same pattern but with a smaller gain magnitude: Recall@1 improves from `0.737` to `0.760`, Recall@5 improves from `0.883` to `0.895`, and Recall@10 stays fixed at `0.918`. This consistency matters because it suggests the reranker is not merely exploiting one evaluation definition. Instead, it is systematically promoting exact evidence pages inside a fixed candidate pool.

Compared with the older follow-up 1000 result, the disjoint validation outcome is slightly more conservative. The strict top1 gain decreases from `+50` to `+47`, and strict regressions increase from `1` to `2`. Even so, the central conclusion survives the split repair: title overlap remains a useful lightweight reranking signal for evidence retrieval on official FEVER.

The method's main contribution should therefore be described narrowly and accurately:

- it improves evidence retrieval ranking
- it does so with a simple title-aware reranking signal
- it does not constitute a complete end-to-end ChronoRAG system result
- it does not improve top-k coverage in the current setting

# Error Analysis

The disjoint validation confirms that the dominant improvement mode is still rank correction within an already retrieved top-k set. The most common pattern is `surface_title_match`, followed by `exact_gold_promotion` and then `disambiguation`. In practical terms, BM25 often retrieves the correct evidence page somewhere in the candidate list, but not always at rank 1. Title overlap helps when the claim explicitly repeats the entity phrase that is also present in the gold page title.

This pattern is visible in claims such as `Cheese in the Trap (TV series) is a television series.` and `Andrew Kevin Walker is American.` In both types of examples, the baseline top result is semantically nearby but not the exact gold page, while title overlap pushes the exact page to the top. These are retrieval-quality gains, not expanded-recall gains.

The regression profile remains small but is no longer zero-like under validation. Two strict regressions were observed in the disjoint split. Both are interpretable title-driven failures: one over-promotes `New Moon Shine` over `Hourglass (James Taylor album)`, and the other promotes `Fortress 2 (video game)` instead of preserving a strict gold-page hit for `Team Fortress 2`. These failures reinforce the main caveat of the method: strong surface lexical overlap can occasionally favor the wrong nearby page.

# Threats to Validity

The new disjoint validation resolves the most important split-independence issue in the earlier 1000-query follow-up result, but several limits remain.

First, the present evidence is still about evidence retrieval and reranking rather than end-to-end claim verification or answer generation. Any paper draft should frame the contribution as a retrieval-stage gain.

Second, the current result is still based on a single disjoint 1000-query sample rather than repeated seeds or a full-dev evaluation. This is enough for a focused draft, but not enough to claim exhaustive robustness.

Third, the reranker is deliberately lightweight. That is a strength for interpretability and reproducibility, but it also means the contribution should not be overstated as a complete system advance. The correct framing is a simple reranking improvement over BM25 on official FEVER evidence retrieval.

Fourth, the older non-independent follow-up 1000 result should remain in the paper only as supporting context or an auxiliary comparison. The main validation result should now be the disjoint 1000 split.

# Writing Readiness

The project is now in a reasonable state for drafting a second small paper, provided the paper is scoped correctly.

Recommended scope:

- official FEVER evidence retrieval
- BM25 candidate retrieval
- lightweight title-overlap reranking
- strict gold-page ranking improvement

Not yet supported as the primary claim:

- a full ChronoRAG end-to-end system paper
- broad claims about generation quality
- broad claims about dense retrieval or multi-route architectures

In short, the new disjoint validation is strong enough to support a focused draft on lightweight reranking gains in evidence retrieval.
