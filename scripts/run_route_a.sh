#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export CHRONORAG_ROOT="${CHRONORAG_ROOT:-$ROOT_DIR}"

python3 "$CHRONORAG_ROOT/src/eval/eval_main.py" \
  --route routeA \
  --config "$CHRONORAG_ROOT/configs/base.yaml" \
  "$@"
