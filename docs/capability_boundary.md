# Current Version Capability Boundary

## What the current version is good for

- verifying the Route A pipeline wiring
- testing file contracts and run artifact layout
- comparing simple score fusion strategies on a controlled subset
- preparing a base repository for migration to GitHub or another server

## What the current version is not good for

- claiming realistic FEVER leaderboard performance
- evaluating a full Wikipedia-scale retrieval setup
- drawing conclusions about Route B or Route C
- making claims about neural temporal reasoning or learned source trust
- evaluating answer generation quality

## Risk of over-interpretation

- demo results are optimistic by construction
- real FEVER subset results will still be easier than the full benchmark if the corpus is restricted to gold evidence pages
- reliability and temporal scores are hand-written heuristics, so their gains or degradations should be interpreted as pipeline diagnostics rather than final scientific claims
