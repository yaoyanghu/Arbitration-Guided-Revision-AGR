# Route A v3 Repro Runbook

## Environment

Use the existing ChronoRAG environment. No new model or new dataset is required.

## 1. Build The Mainline v3 Subset

```powershell
py -3 -m src.data.build_route_a_temporal_subset_v3
```

Expected outputs:

- [route_a_temporal_v3_subset.jsonl](D:/HUYAOYANG/Work/ChronoRAG/data/processed/route_a_temporal_v3_subset.jsonl)
- [route_a_temporal_v3_corpus.jsonl](D:/HUYAOYANG/Work/ChronoRAG/data/corpus/route_a_temporal_v3_corpus.jsonl)

## 2. Run Route A v3

```powershell
py -3 -m src.eval.eval_route_a_temporal `
  --queries data\processed\route_a_temporal_v3_subset.jsonl `
  --corpus data\corpus\route_a_temporal_v3_corpus.jsonl `
  --index-dir runs\route_a_temporal_v3\index `
  --run-dir runs\route_a_temporal_v3 `
  --top-k 5 `
  --bm25-weight 0.6 `
  --temporal-weight 0.25 `
  --reliability-weight 0.15
```

## 3. Generate v3 Reports

```powershell
py -3 -m src.analysis.route_a_casebook `
  --run-dir runs\route_a_temporal_v3 `
  --report-dir reports\route_a_temporal_v3 `
  --min-query-count 54 `
  --min-temporal-changed 8 `
  --min-reliability-helped 6 `
  --min-pairwise-gain 0.100

py -3 -m src.analysis.route_a_stratified_eval `
  --run-dir runs\route_a_temporal_v3 `
  --output reports\route_a_temporal_v3\STRATIFIED_EVAL.md
```

## 4. Build The Minimal v3 Holdout Slice

```powershell
py -3 -m src.data.build_route_a_temporal_v3_holdout
```

## 5. Run The v3 Holdout Validation

```powershell
py -3 -m src.eval.eval_route_a_temporal `
  --queries data\processed\route_a_temporal_v3_holdout.jsonl `
  --corpus data\corpus\route_a_temporal_v3_holdout_corpus.jsonl `
  --index-dir runs\route_a_temporal_v3_holdout\index `
  --run-dir runs\route_a_temporal_v3_holdout `
  --top-k 5 `
  --bm25-weight 0.6 `
  --temporal-weight 0.25 `
  --reliability-weight 0.15
```

## Frozen Settings

- task contract: unchanged from Route A v2
- top_k: `5`
- bm25_weight: `0.6`
- temporal_weight: `0.25`
- reliability_weight: `0.15`
- retrieval-only / temporal-only / temporal+reliability only

## What Is Frozen

- no Route B or Route C integration
- no new model
- no large benchmark switch
- no large sweep
- no scoring-logic rewrite
