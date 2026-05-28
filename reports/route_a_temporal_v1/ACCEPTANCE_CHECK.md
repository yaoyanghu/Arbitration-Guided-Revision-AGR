# Acceptance Check

## README Acceptance Criteria

1. End-to-end small real subset run: PASS
2. Temporal signal measurably changes ranking: PASS
3. Updated evidence beats retrieval-only baseline: PASS
4. Reliability helps some conflict cases: PASS
5. Per-query inspectable artifacts exist: PASS

## Metrics Snapshot

```json
{
  "query_count": 12,
  "weights": {
    "bm25_weight": 0.6,
    "temporal_weight": 0.25,
    "reliability_weight": 0.15
  },
  "stages": {
    "retrieval_only": {
      "query_count": 12,
      "preferred_top1_rate": 0.75,
      "pairwise_preference_success_rate": 0.8333333333333334,
      "mean_preferred_rank": 1.25,
      "preferred_mrr": 0.875,
      "stale_wins_count": 2
    },
    "temporal_only": {
      "query_count": 12,
      "preferred_top1_rate": 0.9166666666666666,
      "pairwise_preference_success_rate": 1.0,
      "mean_preferred_rank": 1.0833333333333333,
      "preferred_mrr": 0.9583333333333334,
      "stale_wins_count": 0
    },
    "temporal_plus_reliability": {
      "query_count": 12,
      "preferred_top1_rate": 1.0,
      "pairwise_preference_success_rate": 1.0,
      "mean_preferred_rank": 1.0,
      "preferred_mrr": 1.0,
      "stale_wins_count": 0
    }
  },
  "acceptance_snapshot": {
    "temporal_changed_ranking_count": 2,
    "reliability_helped_count": 1,
    "final_better_than_retrieval_count": 3
  }
}
```