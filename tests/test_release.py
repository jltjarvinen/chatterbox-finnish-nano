from pathlib import Path

import pytest

from chatterbox_nano_fi import RELEASE_CHECKPOINT, RELEASE_NAME, RELEASE_T3_SHA256
from chatterbox_nano_fi.release import REQUIRED_MODEL_FILES, release_metadata, validate_model_files

def test_release_identity():
    assert RELEASE_NAME == "v0.1.2"
    assert RELEASE_CHECKPOINT == "v0.1.2"
    assert RELEASE_T3_SHA256 == "5a7fb1eaabff39f22af7274f1a7fc344d2910488c0c5e61c5fb6a863f21bcadc"

def test_release_metadata_identity():
    meta = release_metadata(RELEASE_T3_SHA256)
    assert meta["release"] == "v0.1.2"
    assert meta["release_checkpoint"] == RELEASE_CHECKPOINT
    assert meta["language"] == "fi"
    assert meta["normalization"]["expand_numbers"] is True
    assert meta["normalization"]["language_selector"] is False
    assert meta["sampling_defaults"]["temperature"] == 0.8
    assert meta["sampling_defaults"]["top_p"] == 0.95
    assert meta["sampling_defaults"]["top_k"] == 1000

def test_slim_required_files():
    assert "s3gen_meanflow.safetensors" in REQUIRED_MODEL_FILES
    assert "s3gen.safetensors" not in REQUIRED_MODEL_FILES
    assert "t3_nano_v1.yaml" in REQUIRED_MODEL_FILES

def test_validate_model_files_rejects_incomplete_dir(tmp_path: Path):
    with pytest.raises(RuntimeError, match="missing"):
        validate_model_files(tmp_path)
