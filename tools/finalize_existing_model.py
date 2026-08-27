from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from chatterbox.tts_turbo import ChatterboxTurboTTS

from chatterbox_nano_fi.release import validate_model_files, write_release_metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Finalize an already verified Chatterbox Finnish Nano v0.1.2 model directory without changing weights"
    )
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", default="models/chatterbox-nano-fi-v0.1.2")
    parser.add_argument("--repo-id")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-loader-verify", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    src = Path(args.source).expanduser().resolve()
    out = Path(args.output).expanduser().resolve()
    validate_model_files(src)

    if out.exists():
        if not args.force:
            raise FileExistsError(f"Output exists, pass --force: {out}")
        shutil.rmtree(out)
    shutil.copytree(src, out, symlinks=False)

    checkpoint_sha = write_release_metadata(out, repo_id=args.repo_id)

    if not args.skip_loader_verify:
        model = ChatterboxTurboTTS.from_local(out, device="cpu", nano=True)
        if model.conds is None:
            raise RuntimeError("Release verification failed: built-in conds.pt did not load")

    print(f"Release model: {out}")
    print(f"T3 SHA256: {checkpoint_sha}")
    print("Weights were copied byte-for-byte. Only public release metadata was regenerated.")


if __name__ == "__main__":
    main()
