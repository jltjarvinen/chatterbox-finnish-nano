from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import librosa
import numpy as np
import soundfile as sf


@dataclass(frozen=True)
class AudioStats:
    duration: float
    peak: float
    rms_dbfs: float
    clipped_fraction: float


def _to_numpy(value: Any) -> np.ndarray:
    try:
        import torch

        if torch.is_tensor(value):
            return value.detach().cpu().float().numpy()
    except ImportError:
        pass
    return np.asarray(value, dtype=np.float32)


def decode_audio(value: Any, target_sr: int = 16_000) -> tuple[np.ndarray, int]:
    """Decode common Hugging Face Audio representations without relying on one version."""
    array: np.ndarray
    sample_rate: int

    if hasattr(value, "get_all_samples"):
        samples = value.get_all_samples()
        array = _to_numpy(samples.data)
        sample_rate = int(samples.sample_rate)
    elif isinstance(value, dict) and value.get("array") is not None:
        array = _to_numpy(value["array"])
        sample_rate = int(value["sampling_rate"])
    elif isinstance(value, dict) and value.get("bytes") is not None:
        source = io.BytesIO(value["bytes"])
        try:
            array, sample_rate = sf.read(source, dtype="float32", always_2d=False)
        except Exception:
            source.seek(0)
            import torchaudio

            tensor, sample_rate = torchaudio.load(source)
            array = _to_numpy(tensor)
    elif isinstance(value, dict) and value.get("path"):
        source = value["path"]
        try:
            array, sample_rate = sf.read(source, dtype="float32", always_2d=False)
        except Exception:
            import torchaudio

            tensor, sample_rate = torchaudio.load(source)
            array = _to_numpy(tensor)
    elif isinstance(value, (str, Path)):
        source = str(value)
        try:
            array, sample_rate = sf.read(source, dtype="float32", always_2d=False)
        except Exception:
            import torchaudio

            tensor, sample_rate = torchaudio.load(source)
            array = _to_numpy(tensor)
    else:
        raise TypeError(f"Unsupported audio value: {type(value)!r}")

    array = np.asarray(array, dtype=np.float32)
    if array.ndim == 2:
        array = array.mean(axis=1 if array.shape[1] <= 8 else 0)
    if array.ndim != 1:
        array = np.ravel(array)
    if not np.isfinite(array).all():
        array = np.nan_to_num(array, nan=0.0, posinf=0.0, neginf=0.0)

    if sample_rate != target_sr:
        array = librosa.resample(array, orig_sr=sample_rate, target_sr=target_sr, res_type="kaiser_fast")
        sample_rate = target_sr
    return np.ascontiguousarray(array, dtype=np.float32), sample_rate



def save_wav(path: str | Path, waveform: Any, sample_rate: int) -> Path:
    """Write a waveform as mono/stereo PCM16 WAV without TorchCodec/TorchAudio."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)

    audio = _to_numpy(waveform).astype(np.float32, copy=False)
    if audio.ndim == 2:
        # Chatterbox emits channel-first [C, T]. SoundFile expects [T, C].
        if audio.shape[0] <= 8:
            audio = audio[0] if audio.shape[0] == 1 else audio.T
    if audio.ndim > 2:
        raise ValueError(f"Unsupported waveform shape for WAV output: {audio.shape}")
    if not np.isfinite(audio).all():
        audio = np.nan_to_num(audio, nan=0.0, posinf=1.0, neginf=-1.0)
    audio = np.clip(audio, -1.0, 1.0)
    sf.write(str(out), audio, int(sample_rate), format="WAV", subtype="PCM_16")
    return out

def stats(wav: np.ndarray, sample_rate: int) -> AudioStats:
    wav = np.asarray(wav, dtype=np.float32)
    peak = float(np.max(np.abs(wav))) if wav.size else 0.0
    rms = float(np.sqrt(np.mean(np.square(wav), dtype=np.float64))) if wav.size else 0.0
    rms_dbfs = float(20.0 * np.log10(max(rms, 1e-9)))
    clipped = float(np.mean(np.abs(wav) >= 0.999)) if wav.size else 0.0
    return AudioStats(
        duration=float(len(wav) / sample_rate),
        peak=peak,
        rms_dbfs=rms_dbfs,
        clipped_fraction=clipped,
    )


def exact_duration(wav: np.ndarray, sample_rate: int, seconds: float) -> np.ndarray:
    """Center-crop or zero-pad to an exact duration."""
    target = int(round(sample_rate * seconds))
    if len(wav) > target:
        start = (len(wav) - target) // 2
        wav = wav[start : start + target]
    elif len(wav) < target:
        left = (target - len(wav)) // 2
        right = target - len(wav) - left
        wav = np.pad(wav, (left, right))
    return np.ascontiguousarray(wav, dtype=np.float32)


def trim_silence(wav: np.ndarray, top_db: float | None) -> np.ndarray:
    if top_db is None or len(wav) == 0:
        return wav
    trimmed, _ = librosa.effects.trim(wav, top_db=float(top_db))
    return np.ascontiguousarray(trimmed, dtype=np.float32)


def validate_audio(
    wav: np.ndarray,
    sample_rate: int,
    *,
    min_seconds: float,
    max_seconds: float,
    min_rms_dbfs: float = -45.0,
    max_clipped_fraction: float = 0.005,
) -> tuple[bool, str, AudioStats]:
    info = stats(wav, sample_rate)
    if info.duration < min_seconds:
        return False, "audio_too_short", info
    if info.duration > max_seconds:
        return False, "audio_too_long", info
    if info.rms_dbfs < min_rms_dbfs:
        return False, "audio_too_quiet", info
    if info.clipped_fraction > max_clipped_fraction:
        return False, "audio_clipped", info
    return True, "", info
