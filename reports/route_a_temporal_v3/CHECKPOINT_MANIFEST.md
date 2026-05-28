# Route A v3 Checkpoint Manifest

## Mainline Scope

This checkpoint freezes Route A v3 as the current mainline experiment package.

## Core Data

- [route_a_temporal_v3_subset.jsonl](D:/HUYAOYANG/Work/ChronoRAG/data/processed/route_a_temporal_v3_subset.jsonl)
- [route_a_temporal_v3_corpus.jsonl](D:/HUYAOYANG/Work/ChronoRAG/data/corpus/route_a_temporal_v3_corpus.jsonl)
- [route_a_temporal_v3_subset_manifest.md](D:/HUYAOYANG/Work/ChronoRAG/docs/route_a_temporal_v3_subset_manifest.md)

## Core Code

- [build_route_a_temporal_subset_v3.py](D:/HUYAOYANG/Work/ChronoRAG/src/data/build_route_a_temporal_subset_v3.py)
- [eval_route_a_temporal.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_a_temporal.py)
- [score_temporal_conflict.py](D:/HUYAOYANG/Work/ChronoRAG/src/temporal/score_temporal_conflict.py)
- [score_route_a_reliability.py](D:/HUYAOYANG/Work/ChronoRAG/src/reliability/score_route_a_reliability.py)
- [rerank.py](D:/HUYAOYANG/Work/ChronoRAG/src/rerank/rerank.py)
- [route_a_casebook.py](D:/HUYAOYANG/Work/ChronoRAG/src/analysis/route_a_casebook.py)
- [route_a_stratified_eval.py](D:/HUYAOYANG/Work/ChronoRAG/src/analysis/route_a_stratified_eval.py)

## Run Artifacts

- [metrics.json](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v3/metrics.json)
- [queries.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v3/queries.jsonl)
- [per_query_artifacts.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v3/per_query_artifacts.jsonl)
- [retrieval_results.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v3/retrieval_results.jsonl)
- [temporal_results.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v3/temporal_results.jsonl)
- [reliability_results.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v3/reliability_results.jsonl)
- [reranked_results.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v3/reranked_results.jsonl)

## Reports

- [RESULT_SUMMARY.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3/RESULT_SUMMARY.md)
- [ACCEPTANCE_CHECK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3/ACCEPTANCE_CHECK.md)
- [CASEBOOK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3/CASEBOOK.md)
- [STRATIFIED_EVAL.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3/STRATIFIED_EVAL.md)
- [V2_VS_V3_DIFF.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3/V2_VS_V3_DIFF.md)
- [NEXT_STEP_DECISION.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3/NEXT_STEP_DECISION.md)

## Holdout Robustness Check

- [route_a_temporal_v3_holdout.jsonl](D:/HUYAOYANG/Work/ChronoRAG/data/processed/route_a_temporal_v3_holdout.jsonl)
- [RESULT_SUMMARY.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3_holdout/RESULT_SUMMARY.md)
- [NEXT_STEP_DECISION.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3_holdout/NEXT_STEP_DECISION.md)
