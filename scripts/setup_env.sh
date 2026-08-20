#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

PYTHON=${PYTHON:-python3.12}
if command -v uv >/dev/null 2>&1; then
  uv venv --python "$PYTHON" .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  uv pip install -e '.[dev]' --torch-backend=cpu
else
  "$PYTHON" -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python -m pip install --upgrade pip setuptools wheel
  python -m pip install -e '.[dev]'
fi

echo "Ready. Activate with: source $ROOT/.venv/bin/activate"
