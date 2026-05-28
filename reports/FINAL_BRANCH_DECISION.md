# Final Branch Decision

## Decision

Choose **B 失败**.

## Why

- Route A++ is now a thicker mainline package with fixed dev/test splits and balanced case coverage.
- But the Route B graph-native survival experiment does **not** beat the matched non-graph baseline.
- On the decisive v1 native test, all three systems tie:
  - `A++ best non-graph mainline = 1.000 / 1.000`
  - `matched non-graph conflict aggregator = 1.000 / 1.000`
  - `graph-native consistency / consensus = 1.000 / 1.000`

## Consequence

1. Permanently stop the Route B main-method line.
2. Fix Route B as an `analysis / conflict-focused layer`.
3. Return immediately to **Scheme A**.
4. Keep only Route A++ as the main paper method route.

## New Main Position

- Main method line: Route A++
- Route B role: analysis / conflict-focused layer only
- Route C: still out of scope
