from __future__ import annotations

import argparse
import os
from pathlib import Path

from huggingface_hub import HfApi

from chatterbox_nano_fi.release import validate_model_files, write_release_metadata


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Regenerate the v0.1.0 model card and optionally upload README.md only"
    )
    p.add_argument("--model", default="models/chatterbox-nano-fi-v0.1.0")
    p.add_argument("--repo-id", required=True)
    p.add_argument(
        "--upload",
        action="store_true",
        help="Upload only README.md to the existing Hugging Face model repo.",
    )
    p.add_argument(
        "--commit-message",
        default="Expand Chatterbox Finnish Nano training description",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    model_dir = Path(args.model).expanduser().resolve()
    validate_model_files(model_dir)

    checkpoint_sha = write_release_metadata(model_dir, repo_id=args.repo_id)
    readme = model_dir / "README.md"
    print(f"Regenerated {readme} (T3 SHA256 {checkpoint_sha})")

    if args.upload:
        api = HfApi(token=os.getenv("HF_TOKEN") or None)
        api.upload_file(
            path_or_fileobj=str(readme),
            path_in_repo="README.md",
            repo_id=args.repo_id,
            repo_type="model",
            commit_message=args.commit_message,
        )
        print(f"Uploaded README.md only to {args.repo_id}; model weights and visibility were unchanged")


if __name__ == "__main__":
    main()
