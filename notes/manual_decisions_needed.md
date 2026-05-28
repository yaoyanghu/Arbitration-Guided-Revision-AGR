# Manual Decisions Needed

1. Paper title emphasis
- Should the title emphasize the broader family "title-aware lexical reranking," or should it explicitly foreground the stronger exact-title-boost variant?

2. Main-text method focus
- In the main text, should `routeA_bm25_title_overlap` remain the featured variant because it has the existing significance / case-analysis package, or should `routeA_bm25_exact_title_boost` become the headline method because it is stronger on the nearest-baseline comparison?

3. Main table vs secondary table placement
- Should the exact-title baseline appear in the main results table, or should the paper keep BM25 vs title-overlap as the primary table and present exact-title boost as a nearest-baseline comparison table immediately after?

4. Runtime note
- Do you want to add a lightweight runtime / efficiency note for the reranking variants, even if it is only a short paragraph rather than a full benchmark table?

5. Full-dev mention level
- In the current draft, should full-dev be mentioned only as future robustness work, or as an unfinished supplementary experiment that was attempted but not completed in a usable form?
