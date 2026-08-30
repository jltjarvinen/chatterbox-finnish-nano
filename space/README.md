---
title: Chatterbox Finnish Nano
emoji: "🎙️"
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.3.0
python_version: 3.12.12
app_file: app.py
pinned: false
short_description: Finnish Chatterbox Nano TTS
models:
- JJarvinen/chatterbox-finnish-nano
---

# Chatterbox Finnish Nano Space

This directory is a standalone Hugging Face Gradio Space template for the Finnish Nano model.

## Configuration

1. In the main source repository environment, run `python tools/prepare_space.py`. This copies the pinned Chatterbox runtime into `space/chatterbox/` without installing Chatterbox's PyTorch 2.6 dependency into the Space.
2. Create or update the Gradio Space.
3. Copy the files from this directory to the Space repository.
4. In Space Settings, set `MODEL_ID` to `JJarvinen/chatterbox-finnish-nano`.
5. Select ZeroGPU for the fastest hosted demo. CPU Basic is also supported as a slower fallback.
6. If the model repository is private, add `HF_TOKEN` as a Space Secret with read access to the model.
7. When the model is public, `HF_TOKEN` is not required.

The app supports the built-in Finnish voice and an optional uploaded or microphone reference recording.

Reference conditioning mutates Chatterbox model state, so the Space serializes generation requests and restores the built-in conditioning after every request. This prevents one visitor's reference voice from becoming the next visitor's default voice.

The model repository is downloaded when the Space starts. No training data is needed by the Space. The app selects ZeroGPU or a normal CUDA GPU when available and falls back to CPU automatically.

## Why the Chatterbox runtime is copied

The pinned Chatterbox release dependency normally requests PyTorch 2.6. Current ZeroGPU environments use newer supported PyTorch versions. Installing `chatterbox-tts` normally would therefore replace the ZeroGPU PyTorch runtime with an incompatible version.

`tools/prepare_space.py` copies the already installed pinned Chatterbox Python package into this Space instead. `requirements.txt` then installs the non-PyTorch runtime dependencies only.

## Release

This Space runs Chatterbox Finnish Nano v0.1.3. It pins model revision `v0.1.3` and enables Finnish number expansion by default.
