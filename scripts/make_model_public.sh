#!/usr/bin/env bash
set -euo pipefail
: "${HF_REPO_ID:?Set HF_REPO_ID, for example YOUR_NAMESPACE/chatterbox-finnish-nano}"
python tools/set_model_visibility.py --repo-id "$HF_REPO_ID" --public
