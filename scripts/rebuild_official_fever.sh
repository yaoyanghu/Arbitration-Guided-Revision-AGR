#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export CHRONORAG_ROOT="${CHRONORAG_ROOT:-$ROOT_DIR}"
CONDA_BIN="${CONDA_BIN:-/data/miniconda/bin/conda}"
ENV_NAME="${ENV_NAME:-chronorag}"
VENV_PYTHON="${VENV_PYTHON:-$ROOT_DIR/.venv/bin/python}"

RAW_DIR="${CHRONORAG_ROOT}/data/raw/fever_official"
PROCESSED_DIR="${CHRONORAG_ROOT}/data/processed/fever_official"
CORPUS_DIR="${CHRONORAG_ROOT}/data/corpus/fever_official"
INDEX_DIR="${CHRONORAG_ROOT}/indexes/bm25_fever_official"
WIKI_SOURCE_DIR="${RAW_DIR}/wiki-pages/wiki-pages"
DISJOINT_OUTPUT="${PROCESSED_DIR}/shared_task_dev_disjoint_1000.jsonl"
TUNING_PREDICTIONS="${CHRONORAG_ROOT}/runs/fever_official_route_a/predictions.jsonl"

run_python() {
  if [[ -x "$CONDA_BIN" ]] && "$CONDA_BIN" env list | awk '{print $1}' | grep -Fxq "$ENV_NAME"; then
    "$CONDA_BIN" run -n "$ENV_NAME" python "$@"
    return
  fi
  if [[ -x "$VENV_PYTHON" ]]; then
    "$VENV_PYTHON" "$@"
    return
  fi
  echo "No usable Python environment found."
  echo "Expected conda env '$ENV_NAME' or virtualenv interpreter at $VENV_PYTHON"
  exit 1
}

download_data() {
  mkdir -p "$RAW_DIR"
  cd "$RAW_DIR"
  wget -c https://fever.ai/download/fever/train.jsonl
  wget -c https://fever.ai/download/fever/shared_task_dev.jsonl
  wget -c https://fever.ai/download/fever/shared_task_dev_public.jsonl
  wget -c https://fever.ai/download/fever/shared_task_test.jsonl
  wget -c https://fever.ai/download/fever/wiki-pages.zip
  mkdir -p wiki-pages
  unzip -q -n wiki-pages.zip -d wiki-pages
}

prepare_claims() {
  mkdir -p "$PROCESSED_DIR"
  run_python -m src.data.prepare_fever \
    --source file \
    --input "$RAW_DIR/train.jsonl" \
    --output "$PROCESSED_DIR/train.jsonl" \
    --require-evidence
  run_python -m src.data.prepare_fever \
    --source file \
    --input "$RAW_DIR/shared_task_dev.jsonl" \
    --output "$PROCESSED_DIR/shared_task_dev.jsonl" \
    --require-evidence
  run_python -m src.data.prepare_fever \
    --source file \
    --input "$RAW_DIR/shared_task_dev_public.jsonl" \
    --output "$PROCESSED_DIR/shared_task_dev_public.jsonl" \
    --require-evidence
  run_python -m src.data.prepare_fever \
    --source file \
    --input "$RAW_DIR/shared_task_test.jsonl" \
    --output "$PROCESSED_DIR/shared_task_test.jsonl"
}

build_corpus() {
  run_python -m src.corpus.build_wiki2018_corpus \
    --official-wiki-dir "$WIKI_SOURCE_DIR" \
    --output "$CORPUS_DIR"
}

build_index() {
  run_python -m src.retrieval.build_bm25 \
    --corpus-path "$CORPUS_DIR" \
    --index-dir "$INDEX_DIR" \
    --backend sqlite
}

build_disjoint() {
  if [[ ! -f "$TUNING_PREDICTIONS" ]]; then
    echo "Missing tuning predictions file: $TUNING_PREDICTIONS"
    exit 1
  fi
  run_python -m src.analysis.build_disjoint_validation_split \
    --raw-dev "$RAW_DIR/shared_task_dev.jsonl" \
    --tuning-predictions "$TUNING_PREDICTIONS" \
    --output "$DISJOINT_OUTPUT" \
    --sample-size 1000 \
    --seed 42
}

usage() {
  cat <<EOF
Usage: bash scripts/rebuild_official_fever.sh <step>

Steps:
  download       Download official FEVER raw files and unzip wiki-pages
  prepare        Normalize official FEVER claim files
  corpus         Build normalized official FEVER corpus shards
  index          Build SQLite FTS5 BM25 index
  disjoint       Build disjoint 1000 validation split
  all            Run download -> prepare -> corpus -> index -> disjoint
EOF
}

main() {
  local step="${1:-}"
  case "$step" in
    download)
      download_data
      ;;
    prepare)
      prepare_claims
      ;;
    corpus)
      build_corpus
      ;;
    index)
      build_index
      ;;
    disjoint)
      build_disjoint
      ;;
    all)
      download_data
      prepare_claims
      build_corpus
      build_index
      build_disjoint
      ;;
    *)
      usage
      exit 1
      ;;
  esac
}

main "$@"
