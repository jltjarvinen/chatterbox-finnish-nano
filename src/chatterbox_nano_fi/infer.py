from __future__ import annotations

import argparse
import json
import logging
import os
import random
import secrets
from pathlib import Path

import numpy as np
import torch
from huggingface_hub import snapshot_download

from chatterbox.tts_turbo import ChatterboxTurboTTS

from .audio import save_wav
from .text import normalize_finnish, split_for_tts

LOGGER = logging.getLogger("chatterbox_nano_fi.infer")


def _prepare_conditionals_float32(model: ChatterboxTurboTTS, reference_audio: str) -> None:
    """Run upstream reference conditioning while forcing resampling output to float32."""
    import chatterbox.tts_turbo as tts_turbo

    original_resample = tts_turbo.librosa.resample

    def _resample_float32(*args, **kwargs):
        return np.asarray(original_resample(*args, **kwargs), dtype=np.float32)

    tts_turbo.librosa.resample = _resample_float32
    try:
        model.prepare_conditionals(reference_audio, norm_loudness=True)
    finally:
        tts_turbo.librosa.resample = original_resample


def select_device(requested: str) -> str:
    if requested != "auto":
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def resolve_model(model_ref: str) -> Path:
    path = Path(model_ref).expanduser()
    if path.is_dir():
        return path.resolve()
    return Path(
        snapshot_download(
            repo_id=model_ref,
            token=os.getenv("HF_TOKEN") or None,
            allow_patterns=[
                "*.safetensors",
                "*.json",
                "*.txt",
                "*.pt",
                "*.model",
                "*.yaml",
                "README.md",
                "LICENSE*",
            ],
        )
    )


def load_fi_config(model_dir: Path) -> dict:
    path = model_dir / "fi_config.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def load_model(model_dir: Path, *, reference_audio: str | None, device: str) -> ChatterboxTurboTTS:
    LOGGER.info("Loading Finnish Nano model on %s", device)
    model = ChatterboxTurboTTS.from_local(model_dir, device=device, nano=True)
    if reference_audio:
        LOGGER.info("Using reference audio conditioning: %s", reference_audio)
        _prepare_conditionals_float32(model, reference_audio)
    elif model.conds is None:
        raise ValueError(
            "No --reference-audio was provided and this model has no built-in conds.pt. "
            "Pass a clean reference WAV longer than five seconds."
        )
    else:
        LOGGER.info("Using built-in Nano voice conditioning from conds.pt")
    return model


def synthesize_loaded(
    *,
    model: ChatterboxTurboTTS,
    text: str,
    output: Path,
    expand_numbers: bool,
    max_chars: int,
    pause_seconds: float,
    temperature: float,
    top_p: float,
    top_k: int,
    repetition_penalty: float,
) -> Path:
    normalized = normalize_finnish(text, expand_numbers=expand_numbers)
    if not normalized:
        raise ValueError("Text is empty after normalization")
    chunks = split_for_tts(normalized, max_chars=max_chars)
    LOGGER.info("Synthesizing %s chunk(s)", len(chunks))

    waves: list[torch.Tensor] = []
    for index, chunk in enumerate(chunks):
        LOGGER.info("Chunk %s/%s: %s", index + 1, len(chunks), chunk)
        wave = model.generate(
            chunk,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
        ).cpu()
        waves.append(wave)
        if index + 1 < len(chunks) and pause_seconds > 0:
            waves.append(torch.zeros(1, int(round(model.sr * pause_seconds))))
    combined = torch.cat(waves, dim=-1)
    return save_wav(output, combined, model.sr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Finnish speech synthesis with Chatterbox Nano v0.1")
    parser.add_argument("--model", required=True, help="Local exported model directory or Hugging Face model repo ID")
    parser.add_argument(
        "--reference-audio",
        help="Optional reference WAV. If omitted, the release uses its built-in zero-shot conditioning.",
    )
    parser.add_argument("--text", required=True)
    parser.add_argument("--output", default="finnish-nano.wav")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda", "mps"])
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Sampling seed. Omit for a fresh random seed; set a value for reproducible output.",
    )
    parser.add_argument("--expand-numbers", action="store_true")
    parser.add_argument("--max-chars", type=int, default=220)
    parser.add_argument("--pause-seconds", type=float, default=0.18)
    parser.add_argument("--temperature", type=float, default=0.75)
    parser.add_argument("--top-p", type=float, default=0.92)
    parser.add_argument("--top-k", type=int, default=600)
    parser.add_argument("--repetition-penalty", type=float, default=1.2)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    seed = int(args.seed) if args.seed is not None else secrets.randbits(32)
    LOGGER.info("Sampling seed: %s", seed)
    random.seed(seed)
    np.random.seed(seed % (2**32))
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    model_dir = resolve_model(args.model)
    fi_config = load_fi_config(model_dir)
    expand_numbers = args.expand_numbers or bool(fi_config.get("normalization", {}).get("expand_numbers", False))
    model = load_model(model_dir, reference_audio=args.reference_audio, device=select_device(args.device))
    output = synthesize_loaded(
        model=model,
        text=args.text,
        output=Path(args.output),
        expand_numbers=expand_numbers,
        max_chars=args.max_chars,
        pause_seconds=args.pause_seconds,
        temperature=args.temperature,
        top_p=args.top_p,
        top_k=args.top_k,
        repetition_penalty=args.repetition_penalty,
    )
    LOGGER.info("Wrote %s", output)


if __name__ == "__main__":
    main()
