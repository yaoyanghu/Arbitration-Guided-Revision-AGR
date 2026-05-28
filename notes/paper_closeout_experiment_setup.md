# Experiment Setup Draft

Formal experiments use a frozen baseline set under matched budgets.

## HOH Main Table

- stronger retrieval baseline
- no-temporal ablation
- no-conflict ablation
- full model

## TempRAGEval Auxiliary Table

- stronger retrieval baseline
- no-temporal ablation
- full model

All variants use the same retrieval depth, evidence bundle size, and answer-output contract. Formal runs are kept separate from pilot runs through frozen configs, frozen dataset manifests, explicit `formal_*` run groups, and dedicated summary files.
