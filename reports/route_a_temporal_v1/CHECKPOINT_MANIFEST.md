# Route A v1 Checkpoint Manifest

## Purpose

This manifest freezes the current Route A v1 checkpoint as an acceptance-stage rollback target.

Route A v1 is preserved for:

- pipeline wiring validation
- subset contract validation
- controlled temporal and reliability diagnosis

It is not the artifact to use for realistic Route B claims.

## 1. Docs

- [route_a_task_contract_v1.md](D:/HUYAOYANG/Work/ChronoRAG/docs/route_a_task_contract_v1.md)
- [route_a_subset_build_plan_v1.md](D:/HUYAOYANG/Work/ChronoRAG/docs/route_a_subset_build_plan_v1.md)
- [route_a_remaining_work_plan_v1.md](D:/HUYAOYANG/Work/ChronoRAG/docs/route_a_remaining_work_plan_v1.md)
- [capability_boundary.md](D:/HUYAOYANG/Work/ChronoRAG/docs/capability_boundary.md)

## 2. Scripts / Src Modules

- [build_route_a_temporal_subset.py](D:/HUYAOYANG/Work/ChronoRAG/src/data/build_route_a_temporal_subset.py)
- [score_temporal_conflict.py](D:/HUYAOYANG/Work/ChronoRAG/src/temporal/score_temporal_conflict.py)
- [score_route_a_reliability.py](D:/HUYAOYANG/Work/ChronoRAG/src/reliability/score_route_a_reliability.py)
- [eval_route_a_temporal.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_a_temporal.py)
- [route_a_casebook.py](D:/HUYAOYANG/Work/ChronoRAG/src/analysis/route_a_casebook.py)

## 3. Dataset / Subset Files

- [route_a_temporal_v1_subset.jsonl](D:/HUYAOYANG/Work/ChronoRAG/data/processed/route_a_temporal_v1_subset.jsonl)
- [route_a_temporal_v1_corpus.jsonl](D:/HUYAOYANG/Work/ChronoRAG/data/corpus/route_a_temporal_v1_corpus.jsonl)

## 4. Runs

- [metrics.json](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1/metrics.json)
- [queries.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1/queries.jsonl)
- [retrieval_results.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1/retrieval_results.jsonl)
- [temporal_results.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1/temporal_results.jsonl)
- [temporal_reranked_results.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1/temporal_reranked_results.jsonl)
- [reliability_results.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1/reliability_results.jsonl)
- [reranked_results.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1/reranked_results.jsonl)
- [per_query_artifacts.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1/per_query_artifacts.jsonl)
- [summary.md](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1/summary.md)

## 5. Logs

- [build_subset.log](D:/HUYAOYANG/Work/ChronoRAG/logs/route_a_temporal_v1/build_subset.log)
- [eval_route_a_temporal.log](D:/HUYAOYANG/Work/ChronoRAG/logs/route_a_temporal_v1/eval_route_a_temporal.log)
- [route_a_casebook.log](D:/HUYAOYANG/Work/ChronoRAG/logs/route_a_temporal_v1/route_a_casebook.log)

## 6. Reports

- [README.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/README.md)
- [ACCEPTANCE_CHECK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/ACCEPTANCE_CHECK.md)
- [CASEBOOK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/CASEBOOK.md)
- [ERROR_TAXONOMY.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/ERROR_TAXONOMY.md)
- [NEXT_STEP_DECISION.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/NEXT_STEP_DECISION.md)

## 7. Checkpoint Interpretation

This v1 checkpoint should be treated as:

- accepted
- frozen
- rollback-safe

It should not be overwritten by Route A v2 or any later Route B work.
