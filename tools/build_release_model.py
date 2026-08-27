from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from huggingface_hub import HfApi, snapshot_download
from safetensors.torch import load_file

from chatterbox.tts_turbo import ChatterboxTurboTTS

from chatterbox_nano_fi import (
    BASE_MODEL_REPO,
    BASE_MODEL_REVISION,
    RELEASE_NAME,
    RELEASE_T3_SHA256,
)

from chatterbox_nano_fi.release import sha256, validate_model_files, write_release_metadata


def fetch_bucket_checkpoint(bucket: str, bucket_path: str, destination: Path) -> None:
    if shutil.which("hf") is None:
        raise RuntimeError("Hugging Face CLI `hf` is required to read the private training bucket")
    uri = f"hf://buckets/{bucket}/{bucket_path}"
    subprocess.run(["hf", "buckets", "cp", uri, str(destination)], check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Chatterbox Finnish Nano v0.1.2")
    parser.add_argument("--checkpoint", help="Local v0.1.2 T3 safetensors. If omitted, fetch from --bucket and --bucket-path.")
    parser.add_argument("--bucket", default=os.getenv("HF_BUCKET"))
    parser.add_argument("--bucket-path", help="Bucket object path. Required with --bucket.")
    parser.add_argument("--output", default="models/chatterbox-nano-fi-v0.1.2")
    parser.add_argument("--repo-id", help="Optional Hugging Face model repo ID; also used in the generated model card")
    parser.add_argument("--push", action="store_true", help="Upload the verified model directory to --repo-id")
    parser.add_argument("--public", action="store_true", help="When creating a repo with --push, make it public")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-loader-verify", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out = Path(args.output).resolve()
    if out.exists():
        if not args.force:
            raise FileExistsError(f"Output exists; pass --force: {out}")
        shutil.rmtree(out)

    with tempfile.TemporaryDirectory(prefix="cbnano-fi-release-") as tmp:
        tmp = Path(tmp)
        if args.checkpoint:
            checkpoint = Path(args.checkpoint).expanduser().resolve()
            if not checkpoint.exists():
                raise FileNotFoundError(checkpoint)
        else:
            if not args.bucket or not args.bucket_path:
                raise ValueError("Set --checkpoint, or set both --bucket and --bucket-path")
            checkpoint = tmp / "release-t3.safetensors"
            print(f"Fetching {args.bucket_path} from bucket {args.bucket}")
            fetch_bucket_checkpoint(args.bucket, args.bucket_path, checkpoint)

        if sha256(checkpoint) != RELEASE_T3_SHA256:
            raise RuntimeError("v0.1.2 checkpoint SHA256 mismatch")

        snapshot = Path(
            snapshot_download(
                repo_id=BASE_MODEL_REPO,
                revision=BASE_MODEL_REVISION,
                token=os.getenv("HF_TOKEN") or None,
                ignore_patterns=["s3gen.safetensors"],
            )
        )
        staging = tmp / "model"
        shutil.copytree(snapshot, staging, symlinks=False)

        (staging / "s3gen.safetensors").unlink(missing_ok=True)

        base_t3 = staging / "t3_nano_v1.safetensors"
        base_keys = set(load_file(str(base_t3), device="cpu"))
        release_keys = set(load_file(str(checkpoint), device="cpu"))
        if base_keys != release_keys:
            missing = sorted(base_keys - release_keys)
            unexpected = sorted(release_keys - base_keys)
            raise RuntimeError(
                f"v0.1.2 checkpoint does not match Nano T3 contract; missing={missing[:8]}, unexpected={unexpected[:8]}"
            )

        shutil.copy2(checkpoint, base_t3)
        validate_model_files(staging)
        checkpoint_sha = write_release_metadata(staging, repo_id=args.repo_id)

        if not args.skip_loader_verify:
            print("Verifying exported model with ChatterboxTurboTTS.from_local(..., nano=True) on CPU")
            model = ChatterboxTurboTTS.from_local(staging, device="cpu", nano=True)
            if model.conds is None:
                raise RuntimeError("Release verification failed: built-in conds.pt did not load")

        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staging, out, symlinks=False)
        print(f"Release model: {out}")
        print(f"T3 SHA256: {checkpoint_sha}")

    if args.push:
        if not args.repo_id:
            raise ValueError("--push requires --repo-id")
        api = HfApi(token=os.getenv("HF_TOKEN") or None)
        api.create_repo(args.repo_id, repo_type="model", private=not args.public, exist_ok=True)
        api.upload_folder(
            repo_id=args.repo_id,
            repo_type="model",
            folder_path=str(out),
            commit_message=f"Publish Chatterbox Finnish Nano {RELEASE_NAME}",
        )
        print(f"Uploaded model to {args.repo_id}")


if __name__ == "__main__":
    main()
