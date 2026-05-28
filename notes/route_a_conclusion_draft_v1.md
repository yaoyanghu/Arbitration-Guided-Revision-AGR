# Route A Conclusion Draft v1

Route A is the current mainline experiment package. On a balanced 54-query temporal-conflict slice, lightweight temporal and source-reliability reranking substantially improve preferred-evidence ranking over retrieval-only BM25 while keeping the retrieval backbone fixed. A separate 18-query held-out slice preserves the same ordering and therefore serves as a robustness confirmation rather than a second main experiment.

The resulting claim is intentionally narrow. Route A shows that lightweight reranking signals can improve evidence ranking in temporal-conflict settings under a fixed retrieval contract. It does not claim a new model, a new benchmark, or broad benchmark-level generalization. Mixed ambiguous cases remain the main unresolved difficulty, and they mark the clearest next pressure point for later work.

If Route B appears in the final paper at all, it should be framed only as an analysis layer for inspecting conflict structure around hard Route A cases. It is not part of the Route A main method or main empirical contribution.
