from __future__ import annotations

import importlib
import importlib.metadata
import json
import shutil
from pathlib import Path

from chatterbox_nano_fi import CHATTERBOX_REVISION


ROOT = Path(__file__).resolve().parents[1]
SPACE = ROOT / "space"
DEST = SPACE / "chatterbox"


def installed_revision() -> str | None:
    try:
        dist = importlib.metadata.distribution("chatterbox-tts")
    except importlib.metadata.PackageNotFoundError:
        return None
    raw = dist.read_text("direct_url.json")
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    vcs = data.get("vcs_info") or {}
    return vcs.get("commit_id")


def main() -> None:
    module = importlib.import_module("chatterbox")
    source = Path(module.__file__).resolve().parent
    if not (source / "tts_turbo.py").is_file():
        raise RuntimeError(f"Installed chatterbox package looks incomplete: {source}")

    revision = installed_revision()
    if revision and revision != CHATTERBOX_REVISION:
        raise RuntimeError(
            "Installed chatterbox revision does not match the release pin. "
            f"Expected {CHATTERBOX_REVISION}, got {revision}."
        )

    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(
        source,
        DEST,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )
    # The vendored runtime is copied as source rather than installed as the
    # chatterbox-tts distribution. Make its version lookup robust in Spaces.
    init_file = DEST / "__init__.py"
    init_text = init_file.read_text(encoding="utf-8")
    if 'version("chatterbox-tts")' in init_text and "PackageNotFoundError" not in init_text:
        init_text = init_text.replace(
            "from importlib.metadata import version",
            "from importlib.metadata import PackageNotFoundError, version",
        )
        init_text = init_text.replace(
            '__version__ = version("chatterbox-tts")',
            'try:\n    __version__ = version("chatterbox-tts")\nexcept PackageNotFoundError:\n    __version__ = "0.0.0+vendored"',
        )
        init_file.write_text(init_text, encoding="utf-8")

    (SPACE / "CHATTERBOX_REVISION.txt").write_text(CHATTERBOX_REVISION + "\n", encoding="utf-8")

    print(f"Copied pinned Chatterbox runtime from {source}")
    print(f"Space runtime ready at {DEST}")
    if revision is None:
        print("Note: installed distribution did not expose a VCS commit ID, so only the package layout was checked.")


if __name__ == "__main__":
    main()
