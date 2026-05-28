# Route A v3 Mainline Claim Freeze

## Formal Mainline Claim

Under the current Route A task contract, a lightweight temporal-conflict reranking pipeline with a small source-reliability prior improves preferred-evidence ranking over retrieval-only BM25 on a balanced real temporal-conflict slice.

## Supported By Current v3 Numbers

- query_count: `54`
- preferred top1: `0.537 -> 0.704 -> 0.815`
- pairwise success: `0.667 -> 0.796 -> 0.833`
- preferred MRR: `0.762 -> 0.846 -> 0.907`
- temporal changed ranking count: `9`
- reliability helped count: `8`

## What This Claim Does Not Say

- It does not claim a new model.
- It does not claim a new benchmark.
- It does not claim Route B is part of the main method.
- It does not claim Route C.
- It does not claim broad external validity beyond the current real temporal-conflict slices.

## What Is Frozen Now

- Route A task definition
- Route A v3 subset and held-out validation package
- scoring components:
  - BM25 retrieval
  - temporal signal
  - source reliability prior
- current weights:
  - bm25 `0.6`
  - temporal `0.25`
  - reliability `0.15`

## What Is Now Prohibited From Casual Change

- changing the task contract
- replacing the model stack
- swapping to a different large dataset
- introducing Route B / Route C into the Route A mainline
- large hyperparameter sweep before checkpoint use
