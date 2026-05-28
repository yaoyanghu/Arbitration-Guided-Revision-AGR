# ChronoRAG

ChronoRAG is a portable experiment scaffold for temporal-conflict RAG research. This repository is structured so it can be deployed first on a rented cloud GPU server and later moved to a school server or GitHub with minimal path changes.

## Recommended project root

Primary path used for deployment compatibility:

```bash
/home/huyaoyang/Projects/ChronoRAG
```

If the target machine uses another home directory, keep the `ChronoRAG` folder name unchanged and update only the absolute parent path in configs or environment variables.

## Project layout

```text
ChronoRAG/
  configs/
  data/
  corpus/
  indexes/
  src/
  scripts/
  experiments/
  outputs/
  logs/
  reports/
  docs/
  tests/
```

## Current status

Completed modules:

- FEVER input normalization for demo data and real FEVER ingestion entry points
- corpus interface with demo corpus support and explicit missing-data errors
- BM25 index build/load/search
- rule-based temporal score
- rule-based source reliability score
- score fusion rerank
- Route A run orchestration and artifact export under `runs/{exp_name}/`

Not completed:

- Route B
- Route C
- dense retrieval
- generation
- evidence graph
- learned temporal model
- learned reliability model
- full Wikipedia 2018 corpus support
- HoH ingestion

## Demo vs real data

Demo data:

- `data/demo/fever_raw_demo.jsonl`
- `data/demo/demo_corpus_source.jsonl`
- hand-curated, tiny, only for smoke testing
- expected to produce near-perfect retrieval because claims and corpus were written to align

Real FEVER subset:

- sourced from the real FEVER dataset, preferably `labelled_dev`
- claims and labels are real
- evidence titles come from FEVER annotations
- if a local Wikipedia 2018 dump is unavailable, the minimal real corpus is constructed only from gold evidence pages, so it is still much smaller and easier than the full benchmark corpus

## Demo Run

Demo preparation:

```bash
bash scripts/bootstrap_env.sh
bash scripts/check_env.sh
bash scripts/prepare_all.sh
python3 -m src.data.prepare_fever --input data/demo/fever_raw_demo.jsonl --output data/processed/fever/fever.jsonl --sample-size 3 --seed 42
python3 -m src.corpus.build_wiki2018_corpus --use-demo --output data/corpus/demo_corpus.jsonl
```

Demo Route A:

```bash
bash scripts/run_route_a.sh --exp-name fever_demo_route_a
```

Remote demo Route A:

```bash
cd /home/huyaoyang/Projects/ChronoRAG
export CHRONORAG_ROOT=/home/huyaoyang/Projects/ChronoRAG
/data/miniconda/bin/conda run -n chronorag python -m src.eval.eval_main --route routeA --config configs/base.yaml --exp-name fever_demo_route_a_remote
```

Install optional research dependencies only when needed:

```bash
source /data/miniconda/etc/profile.d/conda.sh
conda activate chronorag
pip install -r requirements.full.txt
```

If Conda is unavailable on the target machine, `bash scripts/bootstrap_env.sh`
will automatically fall back to a local virtual environment at `.venv/`.

## Current scope

This initial version focuses on:

- portable directory creation
- environment and GPU checks
- a minimal runnable Route A: FEVER small sample or real FEVER subset + corpus interface + BM25 + rule-based temporal and reliability scoring + basic evaluation
- a lightweight default environment that is easier to reproduce on small rented GPUs

## Data status

- No real Wikipedia 2018 dump is bundled in this repository.
- `src/corpus/build_wiki2018_corpus.py` will raise a clear error unless you pass `--input <corpus.jsonl>` or `--use-demo`.
- A small demo corpus is bundled only for smoke testing.
- HoH is not implemented in the current minimal Route A and is not downloaded or fabricated here.

## Capability boundary

This version can:

- run a minimal Route A retrieval pipeline
- export stage-by-stage jsonl artifacts
- compare BM25, temporal fusion, and temporal plus reliability fusion on a small FEVER setup

This version cannot:

- support claims with no retrievable evidence corpus beyond what you explicitly build
- claim benchmark-level FEVER performance
- replace a full Wikipedia 2018 retrieval benchmark
- support Route B or Route C conclusions
- support learned scoring or generation quality claims

## Notes for migration

- Keep the repository root folder name as `ChronoRAG`.
- Prefer environment variables such as `CHRONORAG_ROOT` over hard-coded paths.
- Commit code and configs, but do not commit large data, indexes, logs, or generated outputs.
