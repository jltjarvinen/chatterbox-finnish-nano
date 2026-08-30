# Chatterbox Finnish Nano

**v0.1.3** is a Finnish-only adaptation of Chatterbox Nano for low-latency
conversational TTS.

Canonical public T3: **FP16**

T3 SHA256:

```text
d25e3ac95eefefb58c40ad4d5a47b4fa621bc1bd92e91f2d904f622d5458ad26
```

## Links

- Model: https://huggingface.co/JJarvinen/chatterbox-finnish-nano
- GGUF: https://huggingface.co/JJarvinen/chatterbox-finnish-nano-GGUF
- Demo: https://huggingface.co/spaces/JJarvinen/chatterbox-finnish-nano

## Install

```bash
git clone https://github.com/jltjarvinen/chatterbox-finnish-nano.git
cd chatterbox-finnish-nano
git checkout v0.1.3
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

Reference conditioning remains available through `--reference-audio`.

## Automatic evaluation

The v0.1.3 final gate was evaluated at FP16 runtime precision.

Finnish quality set:

| Metric | Result |
| --- | ---: |
| prompts | 12 |
| WER | 8.22% |
| CER | 0.95% |
| normalized exact transcript rate | 75% |

Finnish EOS-ASR set: WER 8.48%, CER 1.38%, exact 60/100.

Endpoint safety gate: 100 Finnish + 100 English regression-canary generations.
It produced 0 generation-limit hits, 0 premature >1 s cases, 0 audio tails >1 s,
and a maximum measured tail of 0.78 s.

These are ASR-based intelligibility proxies, not MOS.

See [docs/V0.1.3_EVAL.md](docs/V0.1.3_EVAL.md).

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
  -> constrained EOS projection
  -> v0.1.3
```

The final projection only changes the EOS behavior of the T3 release candidate.
The locked F32 source projection SHA256 is `5a8bf48cc23938bcf462c26d10a5686616c2081dea94d0a0da983ff590f3fe35`.

See [docs/TRAINING.md](docs/TRAINING.md).

## Slim runtime package

The pinned Nano loader uses `s3gen_meanflow.safetensors`. It does not request
the older `s3gen.safetensors` file.

The final release omits only the unused legacy `s3gen.safetensors`. All other
runtime files are retained, including `t3_nano_v1.yaml`.

## GGUF / CrispASR

CrispASR supports Chatterbox Nano directly. The GGUF release contains the custom
Finnish Nano T3 in F16, Q8_0 and Q4_K forms. Nano reuses the unchanged Chatterbox
Turbo MeanFlow S3Gen companion. It is not duplicated in the Finnish GGUF repo.

See the GGUF model card for exact commands.

## Known limitations

T3 generation is autoregressive and stochastic, so different seeds can produce
different speech. The v0.1.3 200-case endpoint release gate did not observe any
>1 s audio tails or >1 s premature cases, but this is a finite validation set,
not a proof that no stochastic outlier can occur.

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
