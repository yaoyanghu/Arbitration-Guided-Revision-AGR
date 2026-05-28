#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONDA_BIN="${CONDA_BIN:-/data/miniconda/bin/conda}"
ENV_NAME="${ENV_NAME:-chronorag}"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/.venv}"

if [[ -x "$CONDA_BIN" ]]; then
  if ! "$CONDA_BIN" env list | awk '{print $1}' | grep -Fxq "$ENV_NAME"; then
    "$CONDA_BIN" create -y -n "$ENV_NAME" python=3.10 pip
  else
    echo "Conda environment '$ENV_NAME' already exists; reusing it."
  fi
  "$CONDA_BIN" run -n "$ENV_NAME" python -m pip install --upgrade pip setuptools wheel
  "$CONDA_BIN" run -n "$ENV_NAME" python -m pip install -r "$ROOT_DIR/requirements.txt"

  echo "Core environment ready via conda. Optional research dependencies:"
  echo "  $CONDA_BIN run -n $ENV_NAME python -m pip install -r $ROOT_DIR/requirements.full.txt"
  echo
  echo "Activate with:"
  echo "  source /data/miniconda/etc/profile.d/conda.sh && conda activate $ENV_NAME"
  exit 0
fi

echo "Conda binary not found at $CONDA_BIN"
echo "Falling back to Python venv at $VENV_DIR"

if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
else
  echo "Virtual environment already exists at $VENV_DIR; reusing it."
fi
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r "$ROOT_DIR/requirements.txt"

echo "Core environment ready via venv. Optional research dependencies:"
echo "  source $VENV_DIR/bin/activate && python -m pip install -r $ROOT_DIR/requirements.full.txt"
echo
echo "Activate with:"
echo "  source $VENV_DIR/bin/activate"
