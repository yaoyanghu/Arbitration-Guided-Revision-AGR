# Ablation Draft

The final ablation story is intentionally narrow.

- `temporal` is the strongest independently validated component because it separates from `no_temporal` on both HOH and TempRAGEval.
- `conflict` is validated on HOH, where the full model outperforms `no_conflict`.
- `source/reliability` is not retained as a mainline contribution because it did not separate from the frozen full model during gating or in the final formal setup.

This stop-loss decision improves claim-evidence alignment. It is better to defend a smaller validated contribution than to retain a broader but unsupported full-stack story.
