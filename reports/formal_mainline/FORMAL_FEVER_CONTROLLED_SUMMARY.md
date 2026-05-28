# FEVER Controlled Auxiliary Summary

## Source

- [official_strict_eval_results.json](D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json)

## Retrieval-Only Auxiliary Table

| setting | strict @1 | strict @5 | strict @10 | relaxed @1 | relaxed @5 | relaxed @10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline BM25 | 0.368 | 0.627 | 0.720 | 0.737 | 0.883 | 0.918 |
| BM25 + title overlap rerank | 0.415 | 0.680 | 0.720 | 0.760 | 0.895 | 0.918 |

## Role

- FEVER stays a controlled auxiliary retrieval benchmark
- these numbers are not mixed into the answer-level HOH or TempRAGEval tables
- the role of FEVER is to show preserved retrieval benchmarking competence, not to define the new mainline claim
