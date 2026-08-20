#!/usr/bin/env bash
set -euo pipefail
SOURCE=${SOURCE:-models/chatterbox-nano-fi-v0.1-rc1}
OUTPUT=${OUTPUT:-models/chatterbox-nano-fi-v0.1.0}
ARGS=(--source "$SOURCE" --output "$OUTPUT")
[[ -n "${HF_REPO_ID:-}" ]] && ARGS+=(--repo-id "$HF_REPO_ID")
[[ "${FORCE:-0}" == "1" ]] && ARGS+=(--force)
python tools/finalize_existing_model.py "${ARGS[@]}"
