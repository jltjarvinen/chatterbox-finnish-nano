from __future__ import annotations

import argparse
import os

from huggingface_hub import HfApi


def main() -> None:
    p = argparse.ArgumentParser(description="Change Hugging Face model repository visibility without re-uploading weights")
    p.add_argument("--repo-id", required=True)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--public", action="store_true")
    group.add_argument("--private", action="store_true")
    args = p.parse_args()

    api = HfApi(token=os.getenv("HF_TOKEN") or None)
    api.update_repo_settings(args.repo_id, repo_type="model", private=not args.public)
    print(f"{args.repo_id}: {'public' if args.public else 'private'}")


if __name__ == "__main__":
    main()
