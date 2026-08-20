#!/usr/bin/env bash
set -euo pipefail
MODEL=${MODEL:-models/chatterbox-nano-fi-v0.1.0}
TEXT=${TEXT:-"Hyvää huomenta! Toivottavasti päiväsi alkaa rauhallisesti."}
OUTPUT=${OUTPUT:-finnish-nano.wav}

ARGS=(--model "$MODEL" --text "$TEXT" --output "$OUTPUT")
[[ -n "${REFERENCE_AUDIO:-}" ]] && ARGS+=(--reference-audio "$REFERENCE_AUDIO")
[[ -n "${SEED:-}" ]] && ARGS+=(--seed "$SEED")
[[ -n "${TEMPERATURE:-}" ]] && ARGS+=(--temperature "$TEMPERATURE")
[[ -n "${TOP_P:-}" ]] && ARGS+=(--top-p "$TOP_P")
[[ -n "${TOP_K:-}" ]] && ARGS+=(--top-k "$TOP_K")
[[ -n "${REPETITION_PENALTY:-}" ]] && ARGS+=(--repetition-penalty "$REPETITION_PENALTY")
[[ "${EXPAND_NUMBERS:-0}" == "1" ]] && ARGS+=(--expand-numbers)

cbnano-fi-infer "${ARGS[@]}"
echo "Wrote $OUTPUT"
