from __future__ import annotations

import copy
import os
import random
import secrets
import threading

import gradio as gr
import numpy as np

try:
    import spaces
except ImportError:
    class _SpacesFallback:
        @staticmethod
        def GPU(*args, **kwargs):
            if args and callable(args[0]):
                return args[0]
            return lambda fn: fn

    spaces = _SpacesFallback()

import torch
from huggingface_hub import snapshot_download

from chatterbox.tts_turbo import ChatterboxTurboTTS
from finnish_text import normalize_finnish, split_for_tts

MODEL_ID = os.getenv("MODEL_ID", "").strip()
MODEL_REVISION = os.getenv("MODEL_REVISION", "v0.1.3").strip() or "v0.1.3"
if not MODEL_ID:
    raise RuntimeError("Set the Hugging Face Space variable MODEL_ID to the Finnish Nano model repo ID")

HF_TOKEN = os.getenv("HF_TOKEN") or None
MODEL_DIR = snapshot_download(
    repo_id=MODEL_ID,
    revision=MODEL_REVISION,
    token=HF_TOKEN,
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


def _env_true(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


IS_ZERO_GPU = _env_true("SPACES_ZERO_GPU")
DEVICE = "cuda" if (IS_ZERO_GPU or torch.cuda.is_available()) else "cpu"
print(
    f"Runtime device: {DEVICE} "
    f"(ZeroGPU={IS_ZERO_GPU}, cuda_available={torch.cuda.is_available()})",
    flush=True,
)
MODEL = ChatterboxTurboTTS.from_local(MODEL_DIR, device=DEVICE, nano=True)
BUILTIN_CONDS = copy.deepcopy(MODEL.conds)
GENERATION_LOCK = threading.Lock()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed % (2**32))
    torch.manual_seed(seed)
    if DEVICE == "cuda":
        torch.cuda.manual_seed_all(seed)


def restore_builtin_conditioning() -> None:
    MODEL.conds = copy.deepcopy(BUILTIN_CONDS)


def prepare_reference(reference_audio: str) -> None:
    import chatterbox.tts_turbo as tts_turbo

    original_resample = tts_turbo.librosa.resample

    def resample_float32(*args, **kwargs):
        return np.asarray(original_resample(*args, **kwargs), dtype=np.float32)

    tts_turbo.librosa.resample = resample_float32
    try:
        MODEL.prepare_conditionals(reference_audio, norm_loudness=True)
    finally:
        tts_turbo.librosa.resample = original_resample


@spaces.GPU(duration=120)
def generate(
    text: str,
    reference_audio: str | None,
    temperature: float,
    top_p: float,
    top_k: int,
    repetition_penalty: float,
    seed: int,
    expand_numbers: bool,
):
    """Generate Finnish speech with optional reference voice conditioning."""
    text = str(text or "").strip()
    if not text:
        raise gr.Error("Anna teksti, joka luetaan ääneen.")
    if len(text) > 600:
        raise gr.Error("Pidä teksti enintään 600 merkissä tässä demossa.")

    chosen_seed = int(seed) if int(seed) != 0 else secrets.randbits(32)
    set_seed(chosen_seed)

    normalized = normalize_finnish(text, expand_numbers=bool(expand_numbers))
    chunks = split_for_tts(normalized, max_chars=220)

    with GENERATION_LOCK:
        restore_builtin_conditioning()
        try:
            if reference_audio:
                prepare_reference(reference_audio)

            waves: list[torch.Tensor] = []
            for index, chunk in enumerate(chunks):
                wave = MODEL.generate(
                    chunk,
                    temperature=float(temperature),
                    top_p=float(top_p),
                    top_k=int(top_k),
                    repetition_penalty=float(repetition_penalty),
                ).detach().cpu()
                waves.append(wave)
                if index + 1 < len(chunks):
                    waves.append(torch.zeros(1, int(round(MODEL.sr * 0.18))))

            combined = torch.cat(waves, dim=-1).squeeze(0).float().numpy()
        finally:
            restore_builtin_conditioning()

    mode = "reference voice" if reference_audio else "built-in voice"
    return (MODEL.sr, combined), f"Seed {chosen_seed}. Mode: {mode}."


with gr.Blocks() as demo:
    gr.Markdown(
        """
# Chatterbox Finnish Nano

**Release v0.1.3. Finnish-only. Number expansion is enabled by default.**

Finnish text to speech with the built-in voice or an optional reference recording.
The reference recording is used only for the current generation.
"""
    )

    with gr.Row():
        with gr.Column():
            text = gr.Textbox(
                label="Teksti",
                value="Hyvää huomenta! Toivottavasti päiväsi alkaa rauhallisesti.",
                lines=4,
                max_lines=8,
            )
            reference = gr.Audio(
                sources=["upload", "microphone"],
                type="filepath",
                label="Reference WAV, optional",
            )
            temperature = gr.Slider(
                minimum=0.3,
                maximum=1.2,
                value=0.8,
                step=0.05,
                label="Temperature",
            )
            with gr.Accordion("More options", open=False):
                top_p = gr.Slider(0.5, 1.0, value=0.95, step=0.01, label="Top p")
                top_k = gr.Slider(50, 1000, value=1000, step=10, label="Top k")
                repetition_penalty = gr.Slider(
                    1.0,
                    1.5,
                    value=1.2,
                    step=0.01,
                    label="Repetition penalty",
                )
                seed = gr.Number(value=0, precision=0, label="Seed, 0 means random")
                expand_numbers = gr.Checkbox(value=True, label="Expand numbers in Finnish")
            run = gr.Button("Generate", variant="primary")

        with gr.Column():
            audio = gr.Audio(label="Generated speech")
            status = gr.Markdown()

    gr.Examples(
        examples=[
            ["Tämä on Chatterbox Finnish Nano versio 0.1.3."],
            ["Mitä kuuluu? Toivottavasti päiväsi on sujunut hyvin."],
            ["Tänään on hyvä päivä kokeilla suomenkielistä puhesynteesiä."],
        ],
        inputs=[text],
    )

    run.click(
        fn=generate,
        inputs=[
            text,
            reference,
            temperature,
            top_p,
            top_k,
            repetition_penalty,
            seed,
            expand_numbers,
        ],
        outputs=[audio, status],
        concurrency_limit=1,
    )

demo.queue(max_size=20, default_concurrency_limit=1).launch()
