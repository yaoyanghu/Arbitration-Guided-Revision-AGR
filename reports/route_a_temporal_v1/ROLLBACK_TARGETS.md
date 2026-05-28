# Route A v1 Rollback Targets

## Purpose

This file lists the exact Route A v1 artifacts that should be preserved unchanged as rollback targets.

## Core Rollback Targets

### Data

- [route_a_temporal_v1_subset.jsonl](D:/HUYAOYANG/Work/ChronoRAG/data/processed/route_a_temporal_v1_subset.jsonl)
- [route_a_temporal_v1_corpus.jsonl](D:/HUYAOYANG/Work/ChronoRAG/data/corpus/route_a_temporal_v1_corpus.jsonl)

### Run Outputs

- [metrics.json](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1/metrics.json)
- [per_query_artifacts.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1/per_query_artifacts.jsonl)
- [retrieval_results.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1/retrieval_results.jsonl)
- [temporal_results.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1/temporal_results.jsonl)
- [temporal_reranked_results.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1/temporal_reranked_results.jsonl)
- [reliability_results.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1/reliability_results.jsonl)
- [reranked_results.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1/reranked_results.jsonl)
- [summary.md](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1/summary.md)

### Reports

- [README.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/README.md)
- [ACCEPTANCE_CHECK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/ACCEPTANCE_CHECK.md)
- [CASEBOOK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/CASEBOOK.md)
- [ERROR_TAXONOMY.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/ERROR_TAXONOMY.md)
- [NEXT_STEP_DECISION.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/NEXT_STEP_DECISION.md)

## Preservation Rule

These files define the accepted Route A v1 checkpoint.

For later Route A or Route B work:

- do not overwrite them
- do not rename them
- do not reuse the same run directory for new experiments

All future work must write into new versioned directories such as `route_a_temporal_v2`.
