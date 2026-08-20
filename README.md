# Chatterbox Finnish Nano

**v0.1.0**. A Finnish language adaptation of Chatterbox Nano aimed at low-latency conversational TTS.

The selected release checkpoint is **015b step 20**. It works without a user-provided reference recording by retaining Nano's built-in `conds.pt` conditioning.

## Status

This is a first release, not a perfect Finnish TTS model. Listening tests showed natural Finnish speech and a clear improvement over stock Nano. The remaining observed issues are occasional dropped syllables/short fragments and occasional long quiet or low-level noisy tails.

## Install

Python 3.11 to 3.13 is supported. On the JÄRVIS/BMax development machine the CPU-only `uv` setup is:

```bash
./scripts/setup_env.sh
source .venv/bin/activate
```

Equivalent manual setup:

```bash
uv venv --python python3.12 .venv
source .venv/bin/activate
uv pip install -e '.[dev]' --torch-backend=cpu
```

## Build the release model from the private research bucket

The source repository intentionally contains no model weights. The release builder takes the selected 015b checkpoint from the training bucket, overlays it on the pinned stock Nano snapshot, retains the stock `conds.pt`, checks the T3 key contract and verifies that the public Nano loader can open the result.

```bash
source .venv/bin/activate
export HF_BUCKET="YOUR_BUCKET"

python tools/build_release_model.py \
  --bucket "$HF_BUCKET" \
  --output models/chatterbox-nano-fi-v0.1.0
```

The default bucket object is:

```text
finnish-nano/experiments/real-audio-micro-polish-v1/checkpoints/step-020.safetensors
```

You can also build from a downloaded checkpoint:

```bash
python tools/build_release_model.py \
  --checkpoint /path/to/step-020.safetensors \
  --output models/chatterbox-nano-fi-v0.1.0
```

## Synthesize Finnish without a reference recording

```bash
MODEL=models/chatterbox-nano-fi-v0.1.0 \
TEXT="Hyvää huomenta! Toivottavasti päiväsi alkaa rauhallisesti." \
./scripts/infer.sh
```

or directly:

```bash
cbnano-fi-infer \
  --model models/chatterbox-nano-fi-v0.1.0 \
  --text "Mitä kuuluu? Toivottavasti päiväsi on sujunut hyvin." \
  --output out.wav
```

By default each invocation gets a fresh random sampling seed. For reproducibility:

```bash
cbnano-fi-infer --model models/chatterbox-nano-fi-v0.1.0 \
  --seed 1234 --text "Hei maailma." --output out.wav
```

`--temperature`, `--top-p`, `--top-k` and `--repetition-penalty` are normal inference controls. The v0.1.0 defaults are `0.75 / 0.92 / 600 / 1.2`. These were not exhaustively optimized and are intentionally user-adjustable.

Reference conditioning remains available:

```bash
REFERENCE_AUDIO=/path/to/reference.wav \
MODEL=models/chatterbox-nano-fi-v0.1.0 \
TEXT="Tämä käyttää annettua äänireferenssiä." \
./scripts/infer.sh
```

The built-in zero-shot path is the primary validated release mode.

## Promote an already verified RC1 model

If you already built and listened to the RC1 directory, there is no reason to rebuild the weights. Promote it to the final release metadata without changing any `.safetensors` bytes:

```bash
./scripts/finalize_rc1.sh
```

This copies `models/chatterbox-nano-fi-v0.1-rc1` to `models/chatterbox-nano-fi-v0.1.0`, verifies the Nano loader and regenerates only `README.md`, `fi_config.json` and `RELEASE.json`.

## Publish the model to Hugging Face

Publish the already verified `v0.1.0` model directory **privately first**:

```bash
export HF_REPO_ID=YOUR_NAMESPACE/chatterbox-finnish-nano
./scripts/publish_model.sh
```

The script validates `RELEASE.json`, regenerates the model card with the real repo ID and creates/uploads a private model repo by default. After downloading that private repo once and verifying synthesis, change its visibility without re-uploading the weights:

```bash
export HF_REPO_ID=YOUR_NAMESPACE/chatterbox-finnish-nano
./scripts/make_model_public.sh
```

See [docs/PUBLISHING.md](docs/PUBLISHING.md) for the complete model + source publication flow. The builder also retains `--push` for one-step workflows, but the separate publish command is safer for the first release because it operates on the exact model directory you already listened to.

## Hugging Face Space

The hosted demo is available at [JJarvinen/chatterbox-finnish-nano](https://huggingface.co/spaces/JJarvinen/chatterbox-finnish-nano).

A Gradio Space template is included in [`space/`](space/README.md). Run
`python tools/prepare_space.py` once before copying it to a Space. It supports the built-in Finnish voice, optional reference audio, temperature and
other sampling controls. ZeroGPU is the recommended hosted configuration. The same app also falls back to CPU when ZeroGPU or a normal CUDA GPU is not available.

Set the Space variable `MODEL_ID` to the published model repository ID. If the
model is still private, also add `HF_TOKEN` as a Space Secret with read access.
Once the model is public, the token is no longer required.

The Space restores the built-in conditioning after every request. A reference
voice uploaded by one visitor is therefore not reused for another visitor.

## What was trained

The release is the end result of a two-stage adaptation rather than a direct
fine-tune on a single audiobook.

### Finnish source text

The synthetic training text was built from Finnish prose in Project Gutenberg:

- *Rautatie* (#10481)
- *Seitsemän veljestä* (#11940)
- *Hanna* (#13140)
- *Papin tytär* (#13662)
- *Papin rouva* (#13663)
- *Lyhyitä kertomuksia* (#12612)
- *Lehtori Hellmanin vaimo* (#11295)

The texts were cleaned and split into short sentence/utterance units suitable for
TTS. Most books were used only as text sources. *Rautatie* also supplied the
fixed Finnish reference recording used during synthetic teacher generation and
the cleaned real-audio material used in the final polish stage.

### Chatterbox Multilingual V2 as the synthetic teacher

"V2" in the research notes means **`ResembleAI/Chatterbox-Multilingual-TTS`**,
which we refer to as Chatterbox Multilingual V2 to distinguish it from the
separate `ResembleAI/Chatterbox-Multilingual-TTS-V3` release.

Multilingual V2 already produced good Finnish when conditioned with the selected
Rautatie reference recording. It was therefore used to synthesize roughly
**15,000 unique Finnish utterance targets** from the text corpus. For every
utterance the teacher used the same Rautatie reference and generated its S3
speech-token sequence autoregressively (free-running).

Those generated S3 sequences became the cached hard targets for Nano. Teacher
logits were not used. This makes the main stage a form of **sequence-level
distillation**: V2 first demonstrates how the Finnish sentence should unfold in
S3 token space, and Nano then learns to reproduce those sequences. V2 does not
need to run during the final Nano optimization once the target cache has been
created.

### Full Nano T3 adaptation

The main Finnish training restarted from stock Chatterbox Nano and trained the
complete T3 path used by Nano:

```text
~15k Finnish text + V2 free-running S3 targets
                    ↓
stock Chatterbox Nano
full used T3 trainable
3 epochs @ LR 1e-4
text next-token CE + speech next-token CE
                    ↓
014 epoch 3
```

All 12 GPT-2-small blocks plus the relevant T3 embeddings, heads, conditioning
encoder, positional embedding and final layer norm were trainable. The voice
encoder and S3/MeanFlow waveform-generation path stayed frozen.

The three epoch schedule was informed by the public Danish CoRal Chatterbox Turbo
training recipe, [CoRal-project/roest-v3-chatterbox-350m](https://huggingface.co/CoRal-project/roest-v3-chatterbox-350m),
which reports three epochs at LR `1e-4`. That recipe was used as a starting point
for the schedule. It was not treated as proof that the same setting would be
optimal for Finnish Nano. Listening tests still selected epoch 3 on the Finnish
model itself.

Nano's original built-in `conds.pt` zero-shot conditioning remained usable, and
reference conditioning with a previously unseen speaker was also sanity-tested
successfully.

### Real-audio micro-polish

Finally, the epoch-3 model received a deliberately small update using S3 targets
derived from the cleaned real Rautatie audio:

```text
014 epoch 3
    ↓
real Rautatie S3, clips <= 20 s
20 optimizer steps @ LR 1e-6
speech next-token CE only
trainable: text_emb + last 2 GPT-2 blocks + ln_f
    ↓
015b step 20  ← v0.1.0
```

The speech embedding/head and conditioning encoder were frozen during this stage
to protect the already-good autoregressive speech interface and reference
conditioning. A more aggressive full-T3 real-audio run at LR `1e-5` collapsed
into repetitive speech and was discarded. Continuing the successful micro-polish
to cumulative steps 30/40/60/80 brought no meaningful audible improvement, so
step 20 was selected as the release checkpoint.

See [docs/TRAINING.md](docs/TRAINING.md) for the compact reproducibility-oriented
recipe and the failed experiment that shaped the final polish stage.

## Known limitations

See [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md). In short: occasional syllable drops, occasional trailing quiet/noise, stochastic variation between generations, and intentionally limited Finnish text normalization.

## Research history

The public source repository is deliberately not the full experiment notebook. Historical 006 to 015c scripts, synthetic target caches and training data stay in the private research repository/bucket. This keeps the release runtime understandable while preserving the experiment history separately.

## Licenses and provenance

The source code in this repository is MIT licensed. The generated model directory combines a pinned upstream Chatterbox Nano snapshot with adapted T3 weights. Review upstream model terms and training-source terms before redistribution or commercial use. No training audio or synthetic training corpus is included here. See [docs/LICENSES_AND_PROVENANCE.md](docs/LICENSES_AND_PROVENANCE.md).
