from pathlib import Path

import pytest

from chatterbox_nano_fi import RELEASE_CHECKPOINT, RELEASE_NAME
from chatterbox_nano_fi.release import release_metadata, validate_model_files


def test_release_identity():
    assert RELEASE_NAME == "v0.1.0"
    assert RELEASE_CHECKPOINT == "015b-step-020"


def test_release_metadata_identity():
    meta = release_metadata("abc123")
    assert meta["release"] == "v0.1.0"
    assert meta["release_checkpoint"] == "015b-step-020"
    assert meta["t3_sha256"] == "abc123"
    assert meta["language"] == "fi"


def test_validate_model_files_rejects_incomplete_dir(tmp_path: Path):
    with pytest.raises(RuntimeError, match="missing"):
        validate_model_files(tmp_path)
