from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from huggingface_hub import HfApi

from chatterbox_nano_fi import RELEASE_CHECKPOINT, RELEASE_NAME
from chatterbox_nano_fi.release import validate_model_files, write_release_metadata


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Upload the verified v0.1.0 model directory to Hugging Face")
    p.add_argument("--model", default="models/chatterbox-nano-fi-v0.1.0")
    p.add_argument("--repo-id", required=True)
    p.add_argument("--public", action="store_true", help="Create/publish a public repo. Default is private.")
    p.add_argument("--commit-message", default=f"Publish Chatterbox Finnish Nano {RELEASE_NAME}")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    model_dir = Path(args.model).expanduser().resolve()
    validate_model_files(model_dir)

    metadata_path = model_dir / "RELEASE.json"
    if not metadata_path.exists():
        raise RuntimeError("RELEASE.json missing; finalize/build the v0.1.0 model first")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("release") != RELEASE_NAME or metadata.get("release_checkpoint") != RELEASE_CHECKPOINT:
        raise RuntimeError(
            f"Unexpected release metadata: release={metadata.get('release')!r}, "
            f"checkpoint={metadata.get('release_checkpoint')!r}"
        )

    # Regenerate the card with the real repo ID immediately before upload.
    write_release_metadata(model_dir, repo_id=args.repo_id)

    api = HfApi(token=os.getenv("HF_TOKEN") or None)
    api.create_repo(args.repo_id, repo_type="model", private=not args.public, exist_ok=True)
    # create_repo(..., exist_ok=True) does not reliably change visibility of an
    # already-existing repo, so apply the requested visibility explicitly.
    api.update_repo_settings(args.repo_id, repo_type="model", private=not args.public)
    api.upload_folder(
        repo_id=args.repo_id,
        repo_type="model",
        folder_path=str(model_dir),
        commit_message=args.commit_message,
    )
    visibility = "public" if args.public else "private"
    print(f"Uploaded {RELEASE_NAME} to {args.repo_id} ({visibility})")


if __name__ == "__main__":
    main()
