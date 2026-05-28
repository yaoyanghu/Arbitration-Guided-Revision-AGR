# Route B v3 Holdout Checkpoint Manifest

## Scope

This checkpoint freezes the final Route B prototype state after the held-out hard-subset verification. It is a stopping point for the current Route B method line, not a launch point for a Route B main experiment.

## Inputs

- Route A hardened subset artifacts:
  - [route_a_temporal_v2_subset.jsonl](D:/HUYAOYANG/Work/ChronoRAG/data/processed/route_a_temporal_v2_subset.jsonl)
  - [metrics.json](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v2/metrics.json)
- Held-out hard subset artifacts:
  - [holdout_subset.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_b_graph_v3_holdout/route_a_holdout/holdout_subset.jsonl)
  - [holdout_corpus.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_b_graph_v3_holdout/route_a_holdout/holdout_corpus.jsonl)

## Route B Scripts And Modules

- [build_route_b_local_graph.py](D:/HUYAOYANG/Work/ChronoRAG/src/graph/build_route_b_local_graph.py)
- [build_route_b_local_graph_v2.py](D:/HUYAOYANG/Work/ChronoRAG/src/graph/build_route_b_local_graph_v2.py)
- [eval_route_b_minimal.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_b_minimal.py)
- [route_b_casebook.py](D:/HUYAOYANG/Work/ChronoRAG/src/analysis/route_b_casebook.py)
- [route_b_ablation.py](D:/HUYAOYANG/Work/ChronoRAG/src/analysis/route_b_ablation.py)
- [route_b_matched_baselines.py](D:/HUYAOYANG/Work/ChronoRAG/src/analysis/route_b_matched_baselines.py)

## Run Artifacts

- v1:
  - [runs/route_b_graph_v1](D:/HUYAOYANG/Work/ChronoRAG/runs/route_b_graph_v1)
  - [reports/route_b_graph_v1](D:/HUYAOYANG/Work/ChronoRAG/reports/route_b_graph_v1)
- v2:
  - [runs/route_b_graph_v2](D:/HUYAOYANG/Work/ChronoRAG/runs/route_b_graph_v2)
  - [reports/route_b_graph_v2](D:/HUYAOYANG/Work/ChronoRAG/reports/route_b_graph_v2)
- v3 holdout:
  - [runs/route_b_graph_v3_holdout](D:/HUYAOYANG/Work/ChronoRAG/runs/route_b_graph_v3_holdout)
  - [logs/route_b_graph_v3_holdout](D:/HUYAOYANG/Work/ChronoRAG/logs/route_b_graph_v3_holdout)
  - [reports/route_b_graph_v3_holdout](D:/HUYAOYANG/Work/ChronoRAG/reports/route_b_graph_v3_holdout)

## Key Reports

- [RESULT_SUMMARY.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_b_graph_v3_holdout/RESULT_SUMMARY.md)
- [CASEBOOK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_b_graph_v3_holdout/CASEBOOK.md)
- [NEXT_STEP_DECISION.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_b_graph_v3_holdout/NEXT_STEP_DECISION.md)
- [MATCHED_BASELINES.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_b_graph_v2/MATCHED_BASELINES.md)
- [STRATIFIED_EVAL.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_b_graph_v2/STRATIFIED_EVAL.md)

## Frozen Interpretation

- Route B has reached a defensible prototype checkpoint.
- Route B has not reached a defensible main-experiment checkpoint.
- The held-out result is the governing checkpoint for current Route B status.
