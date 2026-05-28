# Full Dev Confirmation Status

## Scope

This note checks whether the current ChronoRAG workspace can run the fixed-weight full official FEVER dev confirmation experiment for the current paper line:

- task: official FEVER evidence retrieval
- baseline: BM25
- improved: BM25 + title overlap reranking
- fixed weights: `bm25_weight=0.5`, `title_weight=0.5`

No new method, no new tuning, and no route expansion are considered here.

## Environment Check

### Current repository code path

The codebase is functionally ready for a full-dev run:

- [`src/data/prepare_fever.py`](/D:/HUYAOYANG/Work/ChronoRAG/src/data/prepare_fever.py) already supports official FEVER evidence parsing and `--require-evidence`.
- [`src/corpus/build_wiki2018_corpus.py`](/D:/HUYAOYANG/Work/ChronoRAG/src/corpus/build_wiki2018_corpus.py) already supports `--official-wiki-dir` for official FEVER wiki shards.
- [`src/retrieval/search.py`](/D:/HUYAOYANG/Work/ChronoRAG/src/retrieval/search.py) already supports SQLite FTS BM25 search when `bm25_fts.db` exists.
- [`src/analysis/official_strict_revalidation.py`](/D:/HUYAOYANG/Work/ChronoRAG/src/analysis/official_strict_revalidation.py) already supports strict and relaxed re-evaluation for the frozen title-overlap method.

So the blocker is **not code**.

### Local data / index status

The current local workspace does **not** contain the official FEVER assets needed for full-dev execution.

Missing locally:
- `data/raw/fever_official/`
- `data/processed/fever_official/`
- `data/corpus/fever_official/`
- `indexes/bm25_fever_official/bm25_fts.db`

Observed local state:
- only demo / subset corpora are present under `data/`
- only small JSON BM25 indexes are present under `indexes/`
- no full official SQLite BM25 index is present on the current machine

### School server status

The current desktop session does not have an active checked remote environment for the school server, and no valid school-server official FEVER data mount is available in this workspace. Therefore, I cannot truthfully claim that full-dev conditions are currently satisfied on the school server from this session.

### Historical evidence

The repository logs and notes indicate that official FEVER runs were previously executed in another environment. For example:

- [`logs/fever_official_route_a_disjoint_1000_post.log`](/D:/HUYAOYANG/Work/ChronoRAG/logs/fever_official_route_a_disjoint_1000_post.log)
- [`notes/ChronoRAG_操作说明书.md`](/D:/HUYAOYANG/Work/ChronoRAG/notes/ChronoRAG_操作说明书.md)

These show that the pipeline once had access to official data and a large BM25 index, but those assets are not present in the current local workspace now.

## Execution Result

The full official dev confirmation experiment was **not executed in this session**, because the required official FEVER corpus and BM25 index are absent on the current machine, and no active school-server environment could be verified from this workspace.

This is therefore a **blocked run**, not a completed run.

## What Would Be Needed To Run Full Dev

Minimum required assets:

1. Official FEVER claims files under `data/raw/fever_official/`
2. Official FEVER wiki pages extracted under a local directory
3. Normalized corpus shards under `data/corpus/fever_official/`
4. SQLite BM25 index at `indexes/bm25_fever_official/bm25_fts.db`
5. Full processed dev-verifiable query file under `data/processed/fever_official/`

Once these exist, the fixed-weight full-dev confirmation is straightforward and does not require method changes.

## Minimal Execution Plan Once Assets Are Restored

Prepare full official dev verifiable queries:

```bash
py -3 -m src.data.prepare_fever --source file --input data/raw/fever_official/shared_task_dev.jsonl --output data/processed/fever_official/shared_task_dev_verifiable_full.jsonl --require-evidence --seed 42
```

Normalize official FEVER wiki pages:

```bash
py -3 -m src.corpus.build_wiki2018_corpus --official-wiki-dir data/raw/fever_official/wiki-pages/wiki-pages --output data/corpus/fever_official
```

Build official BM25 index:

```bash
py -3 -m src.retrieval.build_bm25 --corpus-path data/corpus/fever_official --index-dir indexes/bm25_fever_official --backend sqlite
```

Run the full-dev BM25 retrieval:

```bash
py -3 -m src.retrieval.search --corpus-path data/corpus/fever_official --index-dir indexes/bm25_fever_official --queries data/processed/fever_official/shared_task_dev_verifiable_full.jsonl --output runs/fever_official_route_a_full_dev/retrieval_results.jsonl --top-k 10
```

Run fixed-weight title-overlap strict evaluation:

```bash
py -3 -m src.analysis.official_strict_revalidation --queries-path data/processed/fever_official/shared_task_dev_verifiable_full.jsonl --run-dir runs/fever_official_route_a_full_dev --bm25-weight 0.5 --title-weight 0.5
```

Run label-wise strict evaluation if desired:

```bash
py -3 -m src.analysis.official_labelwise_strict_eval --queries-path data/processed/fever_official/shared_task_dev_verifiable_full.jsonl --run-dir runs/fever_official_route_a_full_dev --bm25-weight 0.5 --title-weight 0.5
```

## Relation To Current Main Result

Because the full-dev run was not completed here, the current paper should still treat:

- [`runs/fever_official_route_a_disjoint_1000/`](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000)

as the main independent validation result for the title-overlap line.

The intended role of a future full-dev run would be:
- not to replace the disjoint 1000 result
- but to serve as a robustness confirmation / supplementary confirmation on the entire dev-verifiable pool

## Paper Positioning Recommendation

Until the full-dev run is actually restored and executed, the safest paper wording is:

- main result: disjoint 1000 validation
- full-dev confirmation: planned robustness extension, not yet reported

Do **not** write the paper as if the full official dev confirmation has already been completed.

## Bottom Line

- Code readiness: **yes**
- Local official FEVER assets present: **no**
- Verified school-server run condition from this session: **no**
- Full-dev confirmation executed in this session: **no**

Current status: **blocked by missing official data and index assets, not by method or code.**
