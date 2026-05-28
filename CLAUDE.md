# JIIS Evidence Completion Rules

This project supports a JIIS manuscript on fixed-pool answer-level temporal/conflict arbitration for RAG.

Core rules:
1. Do not invent numbers, metrics, baselines, confidence intervals, p-values, or case studies.
2. Do not open new research directions.
3. Do not add new public benchmarks unless explicitly requested.
4. Do not modify retrieval backbone or rebuild retrieval unless explicitly requested.
5. Preserve the fixed evidence pool protocol.
6. Separate strict fixed-pool comparisons from external/inspired pipeline baselines.
7. Label Self-RAG-style, CRAG-like, HyDE-like, and Astute-style variants as inspired controls unless official reproduction evidence exists.
8. Do not promote Route B selective conflict or Route C soft temporal to formal unless existing decision files show positive promotion criteria.
9. Before running any experiment, audit existing outputs and write what is missing.
10. Every result must have:
    - run command
    - input config
    - output directory
    - per-example predictions where available
    - aggregate metrics
    - reproducibility note

Primary target:
Create a JIIS evidence package with verified full ablation, paired bootstrap CI, fair comparator evidence, decision traces, hyperparameter inventory, and manuscript-ready tables.
