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
    "s3gen.safetensors",
    "t3_nano_v1.safetensors",
    "t3_nano_v1.yaml",
    "ve.safetensors",
    "vocab.json",
    "merges.txt",
    "tokenizer_config.json",
    "special_tokens_map.json",
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
        raise RuntimeError(f"Model directory is incomplete; missing: {missing}")


def release_metadata(checkpoint_sha: str) -> dict:
    return {
        "language": "fi",
        "release": RELEASE_NAME,
        "release_checkpoint": RELEASE_CHECKPOINT,
        "base_model": BASE_MODEL_REPO,
        "base_revision": BASE_MODEL_REVISION,
        "chatterbox_revision": CHATTERBOX_REVISION,
        "t3_sha256": checkpoint_sha,
        "zero_shot_conditioning": "built-in conds.pt retained from base Nano",
        "reference_conditioning": "supported and sanity-tested with a previously unseen reference speaker",
        "normalization": {"expand_numbers": False},
        "sampling_defaults": {
            "temperature": 0.75,
            "top_p": 0.92,
            "top_k": 600,
            "repetition_penalty": 1.2,
        },
    }


def model_card(repo_id: str | None, checkpoint_sha: str) -> str:
    title = repo_id or "Chatterbox Finnish Nano v0.1.0"
    model_ref = repo_id or "YOUR_NAMESPACE/chatterbox-finnish-nano"
    return f'''---
language:
- fi
library_name: chatterbox
pipeline_tag: text-to-speech
base_model: {BASE_MODEL_REPO}
license: mit
tags:
- chatterbox
- chatterbox-nano
- finnish
- text-to-speech
- voice-cloning
---

# {title}

Finnish language adaptation of **Chatterbox Nano** for conversational TTS.
It supports both reference-free Finnish speech using the retained built-in Nano
conditioning and optional reference-voice conditioning.

Release: **{RELEASE_NAME}**  
Selected checkpoint: **{RELEASE_CHECKPOINT}**  
T3 SHA256: `{checkpoint_sha}`

## Quick start

```python
from huggingface_hub import snapshot_download
from chatterbox.tts_turbo import ChatterboxTurboTTS
import soundfile as sf

path = snapshot_download("{model_ref}")
model = ChatterboxTurboTTS.from_local(path, device="cpu", nano=True)
wav = model.generate("Hei! Tämä on suomenkielinen Chatterbox Nano.")
sf.write("out.wav", wav.squeeze(0).cpu().float().numpy(), model.sr)
```

No reference recording is required. A new speaker can also be supplied through
Chatterbox Nano's normal reference-conditioning path.

## Links

- [Source code on GitHub](https://github.com/jltjarvinen/chatterbox-finnish-nano)
- [Live demo on Hugging Face Spaces](https://huggingface.co/spaces/JJarvinen/chatterbox-finnish-nano)
- [Base Chatterbox Nano model](https://huggingface.co/ResembleAI/chatterbox-nano)

The Space uses ZeroGPU when available and also supports CPU fallback.

## Training data and recipe

The released model was produced in two training stages: a larger synthetic
Finnish adaptation followed by a very small real-audio polish.

### 1. Finnish text corpus and Multilingual V2 synthetic targets

The text pool was assembled from Finnish prose in Project Gutenberg:

- *Rautatie* (#10481)
- *Seitsemän veljestä* (#11940)
- *Hanna* (#13140)
- *Papin tytär* (#13662)
- *Papin rouva* (#13663)
- *Lyhyitä kertomuksia* (#12612)
- *Lehtori Hellmanin vaimo* (#11295)

The source texts were cleaned and split into short TTS-friendly utterances. The
books contributed text. *Rautatie* additionally provided the fixed Finnish
reference recording used for teacher synthesis and the real-audio material used
later for the final micro-polish.

The teacher was **Chatterbox Multilingual V2**, specifically
`ResembleAI/Chatterbox-Multilingual-TTS`. During development we called this model
"V2" to distinguish it from the separately released
`ResembleAI/Chatterbox-Multilingual-TTS-V3` model.

For each training sentence, Multilingual V2 was conditioned with the same
selected *Rautatie* reference voice and allowed to generate speech tokens
autoregressively. Roughly **15,000 unique free-running S3 speech-token sequences**
were cached. These sampled sequences were then used as hard sequence-level
training targets for Nano. The final Nano training did not use V2 logits, KL
loss, or an online teacher. Once the S3 target cache existed, V2 was no longer
needed for the optimization run.

### 2. Full-T3 Finnish adaptation

Training started from pristine stock Chatterbox Nano. The complete T3 path used
by Nano was trainable. This included all 12 GPT-2-small transformer blocks, the
position embedding, conditioning encoder, text and speech embeddings and heads,
and the final layer norm. The voice encoder and S3/MeanFlow waveform-generation path stayed
frozen.

Nano was trained for **3 epochs at LR `1e-4`** on the ~15k cached V2 sequences,
using joint causal **text next-token CE + speech next-token CE**.

The three epoch schedule was informed by the public Danish CoRal Chatterbox Turbo
training recipe, [CoRal-project/roest-v3-chatterbox-350m](https://huggingface.co/CoRal-project/roest-v3-chatterbox-350m),
which reports three epochs at LR `1e-4`. That recipe was used as a starting point
for the schedule. It was not treated as proof that the same setting would be
optimal for Finnish Nano. Epoch 3 was still selected by listening to the Finnish
model itself.

Nano's original built-in `conds.pt` reference-free conditioning still worked
after this stage and sounded very similar to the Rautatie-conditioned evaluation.

### 3. Real-audio micro-polish

The selected epoch-3 model was then polished using S3 targets derived from the
cleaned real *Rautatie* audio. This stage was intentionally tiny: **20 optimizer
steps at constant LR `1e-6`**, clips limited to 20 seconds, and speech next-token
CE only. Only `text_emb`, the last two GPT-2 blocks and `ln_f` were trainable.
`cond_enc`, `speech_emb`, `speech_head`, `text_head`, `wpe` and the first ten
GPT-2 blocks were frozen.

A more aggressive full-T3 real-audio experiment at LR `1e-5` collapsed into
repetitive speech and is **not** part of this release. Extending the successful
micro-polish beyond step 20 to cumulative steps 30/40/60/80 produced no meaningful
audible improvement, so **step 20** was selected for v0.1.0.

## Validation status

Subjective listening found the selected model natural and clearly intelligible in
Finnish. Built-in zero-shot conditioning and an unseen reference speaker were both
sanity-tested successfully. This is not a formal MOS/WER benchmark release.

## Known limitations

- An occasional syllable or short speech fragment can be dropped.
- Some generations can contain a long quiet or very-low-level noisy tail.
- Autoregressive sampling makes repeated generations differ. Temperature and
  other sampling controls affect stability and expressiveness.
- Finnish text normalization is intentionally small and does not yet cover every
  date, unit, abbreviation or numeric context.

## Provenance and licenses

The upstream Chatterbox Nano model card is MIT licensed. This archive is assembled
from the pinned Chatterbox Nano base snapshot plus the adapted Finnish T3 weights.
No training audio, source-text dump or synthetic S3 target corpus is included in
this model repository. Training-data redistribution rights are separate from the
model artifact and should be reviewed independently.

Runtime source revision: `{CHATTERBOX_REVISION}`  
Base snapshot revision: `{BASE_MODEL_REVISION}`
'''


def write_release_metadata(model_dir: Path, *, repo_id: str | None = None) -> str:
    validate_model_files(model_dir)
    checkpoint_sha = sha256(model_dir / "t3_nano_v1.safetensors")
    metadata = release_metadata(checkpoint_sha)
    (model_dir / "fi_config.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (model_dir / "RELEASE.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (model_dir / "README.md").write_text(model_card(repo_id, checkpoint_sha), encoding="utf-8")
    return checkpoint_sha
