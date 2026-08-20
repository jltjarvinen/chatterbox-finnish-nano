#!/usr/bin/env bash
set -euo pipefail
MODEL=${MODEL:-models/chatterbox-nano-fi-v0.1.0}
: "${HF_REPO_ID:?Set HF_REPO_ID, for example YOUR_NAMESPACE/chatterbox-finnish-nano}"
python tools/update_model_card.py \
  --model "$MODEL" \
  --repo-id "$HF_REPO_ID" \
  --upload
