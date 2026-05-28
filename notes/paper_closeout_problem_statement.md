# Problem Statement Draft

Modern RAG systems are often evaluated on answer accuracy with limited attention to whether the selected evidence is temporally valid or internally consistent. This is especially problematic when retrieved evidence contains stale updates, retrospective mentions, or mutually inconsistent answer-bearing values. New_ChronoRAG targets this gap by upgrading a legacy retrieval-rerank codebase into a grounded answer-level pipeline that retrieves evidence, arbitrates temporal and conflict signals, and generates cited answers.

The resulting problem setting is narrower than fully open-ended long-horizon reasoning, but broader and more realistic than a tiny-candidate reranking setup. The goal is to produce an answer together with the evidence used to support it, while preferring evidence that is temporally appropriate and internally more reliable under competing answer-bearing passages.
