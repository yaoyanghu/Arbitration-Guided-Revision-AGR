# Paper Wording Pack

## A. Recommended Titles

1. Lightweight Title-Aware Lexical Reranking for Official FEVER Evidence Retrieval
2. Improving Strict Evidence-Page Ranking on Official FEVER with Lightweight Title-Aware Lexical Reranking
3. Early-Rank Evidence Retrieval Gains from Lightweight Title-Aware Lexical Reranking on Official FEVER
4. Title-Aware Lexical Reranking for Strict Gold-Page Retrieval on Official FEVER
5. Re-ranking BM25 Candidates with Lightweight Title-Aware Lexical Signals for Official FEVER Evidence Retrieval

## B. Recommended Abstract Opening Paragraph

This paper studies lightweight title-aware lexical reranking for official FEVER evidence retrieval. Starting from a BM25 candidate retriever, we examine whether simple title-aware lexical signals can improve strict gold-page ranking quality without changing candidate-set coverage. On a disjoint 1000-query official FEVER validation split, title-aware reranking improves early-rank evidence retrieval under strict evaluation, while Recall@10 remains unchanged, indicating that the effect comes from reranking rather than broader retrieval coverage.

## C. Recommended Contribution List

1. We isolate a retrieval-stage problem on official FEVER: improving strict gold-page ranking inside a fixed BM25 candidate pool.
2. We show that lightweight title-aware lexical reranking improves early-rank evidence retrieval quality under strict evaluation.
3. We provide a stronger evaluation package for this setting, including strict and relaxed metrics, label-wise analysis, case analysis, and paired significance with bootstrap confidence intervals.
4. We show that among the tested lightweight title-aware lexical heuristics, an exact-title-style boost is stronger than token-level title overlap, which sharpens the paper's claim and clarifies the tradeoff between stronger gain and more conservative behavior.

## D. Recommended Method Naming

- task family: `title-aware lexical reranking`
- baseline: `routeA_bm25`
- variant 1: `routeA_bm25_title_overlap`
- variant 2: `routeA_bm25_exact_title_boost`

Recommended paper phrasing:
- "We evaluate lightweight title-aware lexical reranking variants over BM25 candidates."

Avoid:
- "Our validated method is title overlap."
- "Title overlap is the best lightweight reranker."

## E. Recommended Results Section Opening Paragraph

We evaluate lightweight title-aware lexical reranking on official FEVER evidence retrieval using a disjoint 1000-query validation split. Relative to BM25, the title-overlap variant improves strict Recall@1 from 0.368 to 0.415 and strict Recall@5 from 0.627 to 0.680, while strict Recall@10 remains unchanged at 0.720. This pattern indicates that the gain arises from improved early-rank ordering within a fixed candidate pool rather than from expanded candidate coverage. We further compare title overlap with a nearest exact-title-style lexical baseline and find that exact title boost is stronger in absolute gain, while title overlap behaves as a more conservative alternative.

## F. Recommended Limitations Paragraph

Our results should be interpreted narrowly. First, the paper studies evidence retrieval reranking rather than end-to-end FEVER verification or a complete ChronoRAG system. Second, the main independent result is on a disjoint 1000-query validation split rather than a completed full-dev confirmation. Third, although the title-overlap variant is statistically supported relative to BM25, it is not the strongest tested lightweight title-aware heuristic in the current repository, since an exact-title-style boost achieves larger gains on the same split. The appropriate claim is therefore that lightweight title-aware lexical reranking is effective for official FEVER evidence retrieval, not that title overlap is uniquely optimal.

## G. Reviewer-Facing Defense

We retain the BM25 vs title-overlap main result because it remains a valid and statistically supported independent comparison on the disjoint 1000 split. This comparison is useful for showing that a conservative token-level title-aware signal can improve strict early-rank evidence retrieval over BM25. At the same time, we explicitly include the nearest exact-title baseline because that is the most natural reviewer challenge: a simpler title-aware lexical heuristic may recover the same or larger gain. Including both results strengthens, rather than weakens, the paper. It prevents overclaiming, clarifies the design space of lightweight title-aware rerankers, and grounds the final paper claim at the correct level: title-aware lexical reranking is effective, and exact-title-style boosting is the stronger tested variant in the current study.
