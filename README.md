# Arbitration-Guided Revision (AGR)

This repository contains the code scaffold and paper-facing audit artifacts for the AGR fixed-pool RAG experiments.

AGR studies answer revision under a frozen evidence-pool protocol: the system may revise an initial TP-FP RAG answer using only the already retrieved evidence pool, without issuing new retrieval, rebuilding indexes, or exposing gold answers to prompts.

## What Is Included

- `src/`: core ChronoRAG/AGR experiment modules used during the development of temporal-conflict RAG pipelines.
- `configs/`: experiment and ablation configs.
- `configs/fixed_pool/published_baseline_adaptations.yaml`: fixed-pool protocol config for the published-method adaptation runs.
- `scripts/fixed_pool_baselines/`: reproducibility scripts for Self-Refine-FP, RARR-FP, FaithfulRAG-inspired FP, CRAG-inspired FP evaluator control, evaluation, bootstrap CI, manifest checks, and closure reports.
- `reports/published_baseline_adaptations_20260621/`: lightweight paper-facing result summaries, naming audit, claims audit, runtime table, bootstrap CI table, and qualitative case shortlist.

Large datasets, model checkpoints, indexes, raw predictions, and generated output directories are intentionally not committed.

## Fixed-Pool Protocol

The published baseline adaptation scripts follow these constraints:

- no extra retrieval;
- no index rebuild;
- no external search;
- no gold answer in prompts;
- no AGR candidate score, candidate family, arbitration margin, trigger reason, or update policy exposed to published-method baselines;
- all runs should record `llm_calls`, token counts, latency, parse status, answer-change status, and `no_extra_retrieval=true`.

The default server-side project root used during the experiments was:

```bash
/home/huyaoyang/Projects/flashrag_project_20251213/New_ChronoRAG
```

Update `configs/fixed_pool/published_baseline_adaptations.yaml` before running on a new machine.

## Main Fixed-Pool Scripts

```bash
# Build or inspect the frozen manifest
python -m scripts.fixed_pool_baselines.build_fixed_pool_manifest

# Validate fixed-pool foundation artifacts
python -m scripts.fixed_pool_baselines.smoke_test_foundation

# Run fixed-pool adaptations
python -m scripts.fixed_pool_baselines.run_self_refine_fp --dataset hoh --dry-run 5
python -m scripts.fixed_pool_baselines.run_rarr_fp --dataset hoh --dry-run 5
python -m scripts.fixed_pool_baselines.run_faithfulrag_fp --dataset hoh --dry-run 5
python -m scripts.fixed_pool_baselines.run_crag_fp_evaluator_control --dataset hoh --dry-run 5

# Evaluate predictions
python -m scripts.fixed_pool_baselines.evaluate_fixed_pool_predictions --help

# Generate final closure/audit tables from existing outputs
python -m scripts.fixed_pool_baselines.nightly_full_closure
```

Full LLM runs are expensive and depend on local model checkpoints; dry-runs and manifest checks should be used first.

## Paper-Facing Result Snapshot

The latest checked closure package reported:

- prediction grid: 27/27 complete;
- paired bootstrap rows: 108 with 10,000 resamples, seed 42;
- strongest non-AGR baseline: TP-FP RAG;
- AGR macro performance over HOH-1024, TempRAGEval-1244, and TimeQA-500: 34.88 EM / 47.25 F1;
- TP-FP RAG macro performance: 28.88 EM / 37.27 F1;
- AGR gain over strongest non-AGR baseline: +6.00 EM / +9.99 F1.

See `reports/published_baseline_adaptations_20260621/` for the method naming audit, claims audit, main table, runtime table, bootstrap CI table, and case shortlist.

## Data And Model Requirements

The scripts expect local fixed-pool inputs, retrieved evidence, TP-FP/AGR prediction files, and local LLM checkpoints. The experiment server used:

- HOH-1024;
- TempRAGEval-1244;
- TimeQA-500;
- optional ArchivalQA-derived-500 appendix checks;
- Qwen2.5-7B-Instruct as the primary fixed-pool adaptation model.

These assets are not bundled in the repository. Configure their paths in `configs/fixed_pool/published_baseline_adaptations.yaml`.

## Repository Hygiene

The `.gitignore` excludes heavy and generated artifacts such as:

- `outputs/`;
- `data/`;
- `indexes/`;
- `models/`;
- `logs/`;
- Python caches and local virtual environments.

Commit code, configs, and small audit summaries only.
