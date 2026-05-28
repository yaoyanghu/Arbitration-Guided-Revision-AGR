# Route A v4 Acceptance Check

- test query count >= 60: `PASS`
- temporal changed ranking count > 0: `PASS`
- reliability helped count > 0: `PASS`
- retrieval_only < temporal_only <= temporal_plus_reliability on test top1: `FAIL`
- temporal + reliability > recency_only and reliability_only on test top1: `PASS`