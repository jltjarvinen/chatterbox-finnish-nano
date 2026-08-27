from __future__ import annotations

import hashlib
import json
from pathlib import Path

from . import (
    BASE_MODEL_REPO,
    BASE_MODEL_REVISION,
    CHATTERBOX_REVISION,
    RELEASE_CHECKPOINT,
    RELEASE_NAME,
)

REQUIRED_MODEL_FILES = (
    "conds.pt",
    "s3gen_meanflow.safetensors",
    "t3_nano_v1.safetensors",
    "t3_nano_v1.yaml",
    "ve.safetensors",
    "vocab.json",
    "merges.txt",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "added_tokens.json",
)

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def validate_model_files(model_dir: Path) -> None:
    missing = [name for name in REQUIRED_MODEL_FILES if not (model_dir / name).is_file()]
    if missing:
        raise RuntimeError(f"Model directory is incomplete, missing: {missing}")
    if (model_dir / "s3gen.safetensors").exists():
        raise RuntimeError("v0.1.2 slim package must not contain s3gen.safetensors")

def release_metadata(checkpoint_sha: str) -> dict:
    return {
        "language": "fi",
        "release": RELEASE_NAME,
        "precision": "bf16",
        "release_checkpoint": RELEASE_CHECKPOINT,
        "base_model": BASE_MODEL_REPO,
        "base_revision": BASE_MODEL_REVISION,
        "chatterbox_revision": CHATTERBOX_REVISION,
        "t3_sha256": checkpoint_sha,
        "clean_target_source_sha256": "56b72efe90369e50e0eea35af2ea2fca540a74d84fdbfbd8bc7ef57b0fd4841d",
        "training_rows": 14169,
        "zero_shot_conditioning": "built-in conds.pt retained from base Nano",
        "reference_conditioning": "supported and release-smoke-tested",
        "normalization": {"expand_numbers": True, "language_selector": False},
        "sampling_defaults": {
            "temperature": 0.8,
            "top_p": 0.95,
            "top_k": 1000,
            "repetition_penalty": 1.2,
        },
        "automatic_eval": {
            "wer": 0.10603829160530191,
            "cer": 0.01647537948907812,
            "exact_rate": 0.54,
            "note": "ASR-based intelligibility proxy, not MOS",
        },
        "runtime_package": {
            "meanflow": True,
            "unused_s3gen_safetensors_shipped": False,
        },
    }

def model_card(repo_id: str | None, checkpoint_sha: str) -> str:
    model_ref = repo_id or "JJarvinen/chatterbox-finnish-nano"
    return (
        "---\n"
        "language:\n"
        "- fi\n"
        "library_name: chatterbox\n"
        "pipeline_tag: text-to-speech\n"
        f"base_model: {BASE_MODEL_REPO}\n"
        "license: mit\n"
        "tags:\n"
        "- chatterbox\n"
        "- chatterbox-nano\n"
        "- finnish\n"
        "- text-to-speech\n"
        "- voice-cloning\n"
        "---\n\n"
        "# Chatterbox Finnish Nano v0.1.2\n\n"
        "Finnish-only adaptation of Chatterbox Nano for conversational TTS.\n\n"
        f"Selected checkpoint: `{RELEASE_CHECKPOINT}`\n\n"
        f"T3 SHA256: `{checkpoint_sha}`\n\n"
        "## Automatic evaluation\n\n"
        "| Metric | v0.1.2 BF16 |\n"
        "| --- | ---: |\n"
        "| WER | 0.1060 |\n"
        "| CER | 0.01648 |\n"
        "| normalized exact transcript rate | 54% |\n\n"
        "WER and CER are ASR-based intelligibility proxies, not human MOS measurements.\n\n"
        "## Use\n\n"
        "Install the companion runtime and run:\n\n"
        "```bash\n"
        "cbnano-fi-infer \\\n"
        f"  --model {model_ref} \\\n"
        '  --text "Lämpötila on 21 astetta." \\\n'
        "  --output out.wav\n"
        "```\n\n"
        "Finnish number-to-speech normalization is enabled by default.\n"
        "The FP16 T3 variant is available at model revision `fp16`.\n\n"
        "## Training\n\n"
        "The release uses 14,169 Finnish S3 target sequences from the strict-QC and regeneration pipeline.\n"
        "QC trailing silence was converted to S3-token trimming at 25 Hz before training.\n"
        "Stock Nano was adapted with full-T3 text and speech next-token CE for three epochs at LR 1e-4, "
        "followed by one continuation epoch at LR 1e-5 to zero.\n\n"
        "## Runtime package\n\n"
        "The pinned Nano runtime loads `s3gen_meanflow.safetensors`. "
        "The legacy `s3gen.safetensors` file is unused and intentionally omitted. "
        "All other files are retained, including `t3_nano_v1.yaml`.\n\n"
        "## Links\n\n"
        "- Source: https://github.com/jltjarvinen/chatterbox-finnish-nano\n"
        "- Demo: https://huggingface.co/spaces/JJarvinen/chatterbox-finnish-nano\n"
        "- Base: https://huggingface.co/ResembleAI/chatterbox-nano\n\n"
        f"Base revision: `{BASE_MODEL_REVISION}`\n\n"
        f"Chatterbox runtime revision: `{CHATTERBOX_REVISION}`\n"
    )

def write_release_metadata(model_dir: Path, *, repo_id: str | None = None) -> str:
    validate_model_files(model_dir)
    checkpoint_sha = sha256(model_dir / "t3_nano_v1.safetensors")
    metadata = release_metadata(checkpoint_sha)
    (model_dir / "fi_config.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (model_dir / "RELEASE.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (model_dir / "README.md").write_text(
        model_card(repo_id, checkpoint_sha),
        encoding="utf-8",
    )
    return checkpoint_sha
