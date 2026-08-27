# Chatterbox Finnish Nano

**v0.1.2** is a Finnish-only adaptation of Chatterbox Nano for low-latency
conversational TTS.

T3 SHA256:

```text
5a7fb1eaabff39f22af7274f1a7fc344d2910488c0c5e61c5fb6a863f21bcadc
```

## Links

- Model: https://huggingface.co/JJarvinen/chatterbox-finnish-nano
- FP16 revision: https://huggingface.co/JJarvinen/chatterbox-finnish-nano/tree/fp16
- Demo: https://huggingface.co/spaces/JJarvinen/chatterbox-finnish-nano

## Install

```bash
git clone https://github.com/jltjarvinen/chatterbox-finnish-nano.git
cd chatterbox-finnish-nano
git checkout v0.1.2
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Synthesize

No reference recording is required.

```bash
cbnano-fi-infer \
  --model JJarvinen/chatterbox-finnish-nano \
  --text "Lämpötila on 21 astetta." \
  --output out.wav
```

Finnish number-to-speech expansion is enabled by default. Disable it with
`--no-expand-numbers`.

Release sampling defaults are read from `fi_config.json`:

```text
temperature         0.8
top_p               0.95
top_k               1000
repetition_penalty  1.2
```

Use the validated FP16 T3 revision with:

```bash
cbnano-fi-infer \
  --model JJarvinen/chatterbox-finnish-nano@fp16 \
  --text "Hyvää huomenta." \
  --output out-fp16.wav
```

Reference conditioning remains available through `--reference-audio`.

## Automatic evaluation

A fixed 100-utterance Finnish set was synthesized and scored with
Faster-Whisper large-v3-turbo.

| Metric | v0.1.2 |
| --- | ---: |
| WER | 10.60% |
| CER | 1.65% |
| normalized exact transcript rate | 54% |

These are ASR-based intelligibility proxies, not MOS.

Stock Nano FP16 scored WER 97.94% and CER 34.45% on the same Finnish set.

See [docs/V0.1.2_EVAL.md](docs/V0.1.2_EVAL.md).

## Training

The final clean target set contains 14,169 Finnish utterances from the strict-QC
and regeneration pipeline.

QC trailing silence was converted to S3-token trimming at 25 Hz. The trainer
then appended exactly one speech EOS target after each sequence.

```text
stock Nano
  -> full T3, 3 epochs, LR 1e-4
  -> one continuation epoch, LR 1e-5 to 0
  -> v0.1.2 E4
```

See [docs/TRAINING.md](docs/TRAINING.md).

## Slim runtime package

The pinned Nano loader uses `s3gen_meanflow.safetensors`. It does not request
the older `s3gen.safetensors` file.

The final release removes only:

```text
s3gen.safetensors
```

All other files are retained, including `t3_nano_v1.yaml`.

Package size falls from 2,563,656,642 bytes to 1,507,172,022 bytes, a 41.21%
reduction. Deterministic full and slim tests produced identical T3 tokens and
byte-identical final waveforms.

## Known limitations

T3 generation is autoregressive and stochastic. Rare samples can continue past
the expected end before EOS.

The 100-generation release smoke produced 2 events over the one-second
structured-runaway threshold and 1 over two seconds. It produced no
generation-limit hits and no tail45 events over one second.

Finnish normalization covers common number cases but is not a complete
linguistic normalization engine.

See [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md).

## Provenance

Base: `ResembleAI/chatterbox-nano`

Base revision: `71ccd1d0081b430592cea481f4307e764e07bc64`

Runtime revision: `5de7a54aa4e5e2baadb0182dde554908b48b85c2`

Clean target source SHA256:

```text
56b72efe90369e50e0eea35af2ea2fca540a74d84fdbfbd8bc7ef57b0fd4841d
```
