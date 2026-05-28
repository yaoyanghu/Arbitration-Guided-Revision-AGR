# Main Results Draft

On HOH, the full model improves over both `no_temporal` and `no_conflict`, showing that temporal-aware answer extraction and conflict-aware evidence arbitration each contribute to the final answer-level system. The absolute gains are modest, but they remain visible at formal scale rather than disappearing outside pilot slices.

On TempRAGEval, the full model preserves a gain over `no_temporal`, indicating that the temporal extraction path is not just a dataset-specific artifact. At the same time, TempRAGEval does not provide new independent evidence for conflict arbitration, so the auxiliary temporal result should be presented as support for the temporal component rather than as a second full-stack proof.
