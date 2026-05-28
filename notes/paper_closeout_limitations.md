# Limitations Draft

The current system remains heuristic-heavy in answer extraction and evidence arbitration. Although this keeps the pipeline reproducible and affordable, it also limits generality compared with larger learned generators or rerankers.

The source/reliability path is implemented but not empirically validated as a core answer-level contribution under the current datasets. TempRAGEval validates the temporal component, but it does not independently validate conflict arbitration. FEVER remains retrieval-only auxiliary evidence rather than answer-level mainline support. These limitations should be stated explicitly rather than softened in prose.
