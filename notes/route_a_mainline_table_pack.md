# Route A Mainline Table Pack

## Main Result Table

| split | stage | preferred top1 | pairwise success | mean preferred rank | preferred MRR | stale wins |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| v3 mainline | retrieval-only | 0.537 | 0.667 | 1.500 | 0.762 | 18 |
| v3 mainline | temporal-only | 0.704 | 0.796 | 1.333 | 0.846 | 11 |
| v3 mainline | temporal + reliability | 0.815 | 0.833 | 1.185 | 0.907 | 9 |
| v3 holdout | retrieval-only | 0.500 | 0.667 | 1.500 | 0.750 | 6 |
| v3 holdout | temporal-only | 0.722 | 0.778 | 1.278 | 0.861 | 4 |
| v3 holdout | temporal + reliability | 0.833 | 0.889 | 1.167 | 0.917 | 2 |

## Stratified Case-Type Table

| stage | case type | preferred top1 | pairwise success | mean preferred rank | preferred MRR | improved | regressed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| retrieval-only | clear | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| retrieval-only | reliability-sensitive | 0.611 | 1.000 | 1.389 | 0.806 | 0 | 0 |
| retrieval-only | mixed | 0.000 | 0.000 | 2.111 | 0.481 | 0 | 0 |
| temporal-only | clear | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| temporal-only | reliability-sensitive | 0.722 | 1.000 | 1.278 | 0.861 | 2 | 0 |
| temporal-only | mixed | 0.389 | 0.389 | 1.722 | 0.676 | 7 | 0 |
| temporal + reliability | clear | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| temporal + reliability | reliability-sensitive | 0.944 | 1.000 | 1.056 | 0.972 | 6 | 0 |
| temporal + reliability | mixed | 0.500 | 0.500 | 1.500 | 0.750 | 11 | 0 |

## Error Taxonomy Section

- Mixed ambiguous cases remain the hardest slice.
- Retrieval-only is already perfect on clear updated-vs-stale cases, so most room for improvement lies in reliability-sensitive and mixed cases.
- Reliability priors mainly help near-tie same-year conflicts rather than broad retrieval failures.

## Representative Case Study Section

- Reliability-helped examples:
  - Joe Biden 2021 reliability query
  - Lionel Messi 2023 reliability query
  - Threads 2023 reliability query
- Mixed hard examples that still resist full correction:
  - Joe Biden mixed
  - Lionel Messi mixed
  - Midnights mixed

## Route B As Analysis Layer

If Route B appears at all, it should be described only as an analysis layer for inspecting update / contradiction / corroboration patterns around difficult Route A cases. It is not part of the Route A main result table.
