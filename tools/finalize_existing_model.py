from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from chatterbox.tts_turbo import ChatterboxTurboTTS

from chatterbox_nano_fi import RELEASE_CHECKPOINT, RELEASE_NAME
from chatterbox_nano_fi.release import validate_model_files, write_release_metadata


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Promote an already verified RC model directory to the v0.1.0 release without changing weights"
    )
    p.add_argument("--source", default="models/chatterbox-nano-fi-v0.1-rc1")
    p.add_argument("--output", default="models/chatterbox-nano-fi-v0.1.0")
    p.add_argument("--repo-id", help="Optional Hugging Face repo ID to bake into the generated model card")
    p.add_argument("--force", action="store_true")
    p.add_argument("--skip-loader-verify", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    src = Path(args.source).expanduser().resolve()
    out = Path(args.output).expanduser().resolve()
    validate_model_files(src)

    release_json = src / "RELEASE.json"
    if release_json.exists():
        old = json.loads(release_json.read_text(encoding="utf-8"))
        checkpoint = old.get("release_checkpoint")
        if checkpoint and checkpoint != RELEASE_CHECKPOINT:
            raise RuntimeError(
                f"Refusing to promote unexpected checkpoint {checkpoint!r}; expected {RELEASE_CHECKPOINT!r}"
            )

    if out.exists():
        if not args.force:
            raise FileExistsError(f"Output exists; pass --force: {out}")
        shutil.rmtree(out)
    shutil.copytree(src, out, symlinks=False)

    checkpoint_sha = write_release_metadata(out, repo_id=args.repo_id)

    if not args.skip_loader_verify:
        print("Verifying promoted model with ChatterboxTurboTTS.from_local(..., nano=True) on CPU")
        model = ChatterboxTurboTTS.from_local(out, device="cpu", nano=True)
        if model.conds is None:
            raise RuntimeError("Release verification failed: built-in conds.pt did not load")

    print(f"Release model: {out}")
    print(f"Release: {RELEASE_NAME}")
    print(f"Checkpoint: {RELEASE_CHECKPOINT}")
    print(f"T3 SHA256: {checkpoint_sha}")
    print("Weights were copied byte-for-byte; only release metadata/model card were regenerated.")


if __name__ == "__main__":
    main()
