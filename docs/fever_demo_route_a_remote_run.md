# Demo Run Freeze

This document freezes the current demo Route A state before expanding to a real FEVER subset experiment.

## Verified remote run

- Run directory: `/home/huyaoyang/Projects/ChronoRAG/runs/fever_demo_route_a_remote`
- Verified artifacts:
  - `metrics.json`
  - `retrieval_results.jsonl`
  - `temporal_results.jsonl`
  - `reliability_results.jsonl`
  - `reranked_results.jsonl`
  - `predictions.jsonl`
  - `error_cases.jsonl`

## Metrics snapshot

```json
{
  "query_count": 3,
  "retrieval_hit_at_k": 1.0,
  "reranked_hit_at_k": 1.0,
  "top1_hit_rate": 1.0,
  "top_k": 5
}
```

## Interpretation

- This run is a smoke test, not a benchmark result.
- The demo FEVER file and demo corpus are intentionally aligned.
- Perfect scores here only show that the minimal Route A pipeline is wired correctly.
