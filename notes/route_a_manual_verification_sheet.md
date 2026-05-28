# Route A Manual Verification Sheet

## 1. Table Numbers And Their Source Files

### Mainline Result Table

- Route A v3 mainline numbers
  source:
  [metrics.json](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v3/metrics.json)
  rendered in:
  [route_a_final_main_tables.md](D:/HUYAOYANG/Work/ChronoRAG/notes/route_a_final_main_tables.md)
  [route_a_final_tables.tex](D:/HUYAOYANG/Work/ChronoRAG/notes/route_a_final_tables.tex)

### Held-out Robustness Table

- Route A v3 hold-out numbers
  source:
  [metrics.json](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v3_holdout/metrics.json)
  rendered in:
  [route_a_final_main_tables.md](D:/HUYAOYANG/Work/ChronoRAG/notes/route_a_final_main_tables.md)
  [route_a_final_tables.tex](D:/HUYAOYANG/Work/ChronoRAG/notes/route_a_final_tables.tex)

### Stratified Case-Type Table

- stratified Route A v3 numbers
  source:
  [STRATIFIED_EVAL.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3/STRATIFIED_EVAL.md)
  rendered in:
  [route_a_final_main_tables.md](D:/HUYAOYANG/Work/ChronoRAG/notes/route_a_final_main_tables.md)
  [route_a_final_tables.tex](D:/HUYAOYANG/Work/ChronoRAG/notes/route_a_final_tables.tex)

## 2. Numbers To Verify One By One

- Mainline:
  - retrieval-only top1 `0.537`
  - temporal-only top1 `0.704`
  - temporal + reliability top1 `0.815`
  - retrieval-only pairwise `0.667`
  - temporal-only pairwise `0.796`
  - temporal + reliability pairwise `0.833`
  - preferred MRR `0.762 / 0.846 / 0.907`

- Held-out:
  - retrieval-only top1 `0.500`
  - temporal-only top1 `0.722`
  - temporal + reliability top1 `0.833`
  - retrieval-only pairwise `0.667`
  - temporal-only pairwise `0.778`
  - temporal + reliability pairwise `0.889`

- Stratified:
  - reliability-sensitive final top1 `0.944`
  - mixed final top1 `0.500`
  - mixed retrieval-only top1 `0.000`
  - mixed final pairwise `0.500`
  - reliability-sensitive final pairwise `1.000`

- Acceptance-style supporting numbers:
  - mainline temporal changed ranking count `9`
  - mainline reliability helped count `8`
  - hold-out temporal changed ranking count `4`
  - hold-out reliability helped count `2`

## 3. Statements Most Likely To Overclaim

- “Route A generalizes broadly”
  safer wording:
  Route A is supported on balanced temporal-conflict slices and a small held-out robustness confirmation.

- “The held-out package is a second main experiment”
  safer wording:
  The held-out package is a robustness confirmation.

- “Route B contributes to the main result”
  safer wording:
  Route B appears only as an analysis layer, if mentioned at all.

- “The method solves temporal conflict”
  safer wording:
  The method improves preferred-evidence ranking under the current Route A contract.

## 4. Places Where Wording Must Be Unified

- Use `retrieval-only`, `temporal-only`, and `temporal + reliability` consistently.
- Use `held-out robustness confirmation` consistently, not `secondary experiment`, `extra benchmark`, or `validation benchmark`.
- Use `preferred top1`, `pairwise preference success`, and `preferred MRR` consistently.
- Use `analysis layer` for Route B consistently; avoid `module`, `co-method`, or `second route contribution` unless intentionally clarified.
- Use `balanced temporal-conflict slice` consistently for the Route A v3 mainline package.

## 5. Last Human Checks Before Export

- Compare markdown table values with LaTeX table values line by line.
- Make sure abstract, results, and conclusion all use the same main claim wording.
- Make sure Route C never appears in the final draft.
- Make sure Route B never enters the main result table or method section as a core component.
