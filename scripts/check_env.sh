#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export CHRONORAG_ROOT="${CHRONORAG_ROOT:-$ROOT_DIR}"

echo "== ChronoRAG Environment Check =="
echo "Project root: $CHRONORAG_ROOT"
echo "Current user: $(whoami)"
echo "Hostname: $(hostname)"
echo "Python: $(python3 -V 2>/dev/null || python -V)"
echo "Pip: $(pip3 --version 2>/dev/null || pip --version || echo unavailable)"
echo "Git: $(git --version 2>/dev/null || echo unavailable)"
echo "Disk usage:"
df -h "$CHRONORAG_ROOT" || df -h .

if command -v nvidia-smi >/dev/null 2>&1; then
  echo "GPU:"
  nvidia-smi
else
  echo "GPU: nvidia-smi not found"
fi

if command -v conda >/dev/null 2>&1; then
  echo "Conda: $(conda --version)"
else
  echo "Conda: not in PATH"
fi
