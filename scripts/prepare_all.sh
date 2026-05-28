#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export CHRONORAG_ROOT="${CHRONORAG_ROOT:-$ROOT_DIR}"

mkdir -p \
  "$CHRONORAG_ROOT/configs" \
  "$CHRONORAG_ROOT/data/raw" \
  "$CHRONORAG_ROOT/data/processed" \
  "$CHRONORAG_ROOT/corpus/wiki2018" \
  "$CHRONORAG_ROOT/indexes" \
  "$CHRONORAG_ROOT/src/data" \
  "$CHRONORAG_ROOT/src/corpus" \
  "$CHRONORAG_ROOT/src/retrieval" \
  "$CHRONORAG_ROOT/src/rerank" \
  "$CHRONORAG_ROOT/src/temporal" \
  "$CHRONORAG_ROOT/src/reliability" \
  "$CHRONORAG_ROOT/src/graph" \
  "$CHRONORAG_ROOT/src/generation" \
  "$CHRONORAG_ROOT/src/eval" \
  "$CHRONORAG_ROOT/scripts" \
  "$CHRONORAG_ROOT/experiments" \
  "$CHRONORAG_ROOT/outputs" \
  "$CHRONORAG_ROOT/logs" \
  "$CHRONORAG_ROOT/reports" \
  "$CHRONORAG_ROOT/docs" \
  "$CHRONORAG_ROOT/tests"

echo "Created ChronoRAG scaffold under: $CHRONORAG_ROOT"
