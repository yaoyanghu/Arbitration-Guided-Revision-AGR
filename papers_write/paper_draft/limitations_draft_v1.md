# Limitations Draft V1

This study should be interpreted narrowly. First, it is a retrieval-only paper: we evaluate evidence-page reranking on official FEVER, not end-to-end claim verification accuracy, sentence-level attribution, or a complete ChronoRAG pipeline. The results therefore support conclusions about evidence ranking quality only.

Second, the main independent validation result is anchored on a disjoint 1000-query split rather than a completed full-dev confirmation. This split is sufficient for a stable short-paper claim because it repairs the earlier overlap issue and supports strict evaluation, label-wise analysis, and paired significance. However, it is still narrower than a full-dev robustness confirmation and should be described that way.

Third, the title-overlap variant is not the strongest tested lightweight title-aware heuristic in the current repository. The nearest exact-title-boost baseline is stronger on the same split. For this reason, the paper should avoid presenting title overlap as uniquely optimal. The defensible claim is that lightweight title-aware lexical reranking is effective, with title overlap representing a conservative variant inside that broader family.

Fourth, the current interpretation relies on a fixed BM25 candidate pool. Because Recall@10 remains unchanged, the paper's gains should be understood as reranking improvements rather than evidence-coverage improvements. This makes the contribution clear, but it also narrows the scope of what can be claimed.

Finally, the present draft includes only a lightweight qualitative runtime note rather than a dedicated runtime benchmark. That choice is appropriate for a short paper centered on retrieval quality, but it means efficiency claims should remain modest.
