# Papers Write Asset Pack (ASCII)

This folder is the FEVER short paper writing pack.

## Key subfolders

- `runs/fever_official_route_a_disjoint_1000_main/`
  Main independent validation result. Use this as the primary paper anchor.

- `runs/fever_official_route_a_disjoint_1000_nearest_baseline/`
  Nearest title-aware lexical baseline comparison.

- `runs/fever_official_route_a/`
  500-query tuning and early official baseline artifacts.

- `runs/fever_official_route_a_1000_historical/`
  Historical 1000-query result. Keep as history, not as main validation.

- `notes_core/`
  Core paper-facing notes, significance, case analysis, overlap report, tables.

- `paper_draft/`
  Draft-ready writing files: abstract, introduction, results, limitations, outline, and paper tables.

- `remote_server_snapshot/`
  Small files copied from the school server: run snapshots, notes snapshots, and full-dev log/script snapshot.

## Most important files

1. Main result
- `runs/fever_official_route_a_disjoint_1000_main/official_strict_eval_results.json`

2. Label-wise result
- `runs/fever_official_route_a_disjoint_1000_main/official_labelwise_results.json`

3. Nearest baseline result
- `runs/fever_official_route_a_disjoint_1000_nearest_baseline/nearest_title_baseline_results.json`

4. Significance
- `notes_core/significance_analysis.md`
- `notes_core/significance_table.md`

5. Overlap repair
- `notes_core/overlap_check_report.md`

6. Case analysis
- `notes_core/case_analysis.md`
- `notes_core/case_table.md`

7. Paper writing drafts
- `paper_draft/abstract_draft_v1.md`
- `paper_draft/introduction_draft_v1.md`
- `paper_draft/results_draft_v1.md`
- `paper_draft/limitations_draft_v1.md`
- `paper_draft/final_tables_for_paper.tex`

## Frozen paper claim

Use:
- `lightweight title-aware lexical reranking for official FEVER evidence retrieval`

Do not use:
- `title overlap is the validated best method`

See:
- `notes_core/current_claim_freeze.md`

## Remote sync note

The school server contains larger assets, but this pack only copies paper-relevant small files and result snapshots.
It does not copy the full official dataset, full Wikipedia corpus, or large indexes.

## Writing order

1. Read `notes_core/current_claim_freeze.md`
2. Read `paper_draft/abstract_draft_v1.md`
3. Read `paper_draft/introduction_draft_v1.md`
4. Use `paper_draft/final_tables_for_paper.tex` together with `notes_core/tables_markdown.md`

## Bottom line

This folder is now a usable local paper asset pack for the FEVER short paper.
