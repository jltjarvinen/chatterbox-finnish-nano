#!/usr/bin/env bash
set -euo pipefail
MODEL=${MODEL:-models/chatterbox-nano-fi-v0.1.0}
: "${HF_REPO_ID:?Set HF_REPO_ID, for example YOUR_NAMESPACE/chatterbox-finnish-nano}"
ARGS=(--model "$MODEL" --repo-id "$HF_REPO_ID")
[[ "${PUBLIC:-0}" == "1" ]] && ARGS+=(--public)
python tools/publish_model.py "${ARGS[@]}"
