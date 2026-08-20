# Changelog

## v0.1.0 — 2026-08-20

First public release of Chatterbox Finnish Nano.

- Finnish adaptation of Chatterbox Nano selected from `015b step 20`.
- Reference-free built-in conditioning validated for Finnish conversational speech.
- Optional reference-voice conditioning sanity-tested successfully with an unseen speaker.
- Final recipe: V2 synthetic S3 full-T3 adaptation, followed by a 20-step conservative real-audio micro-polish.
- Random sampling seed by default; reproducible output available with `--seed`.
- Known limitations documented rather than hidden: occasional syllable/fragment drops and occasional quiet/noisy trailing audio.
## 2026-08-20 Space CPU fallback and linking

- Added automatic ZeroGPU, CUDA GPU, and CPU runtime selection to the Space.
- Added PyTorch 2.8+ as a non-downgrading Space dependency so CPU Basic can install Torch.
- Added explicit Hugging Face Space metadata linking the demo to `JJarvinen/chatterbox-finnish-nano`.
- Made `prepare_space.py` patch the vendored Chatterbox version lookup automatically.
- Added the hosted Space demo link to the generated model card.

