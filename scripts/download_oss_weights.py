#!/usr/bin/env python
"""Utility to download OSS model checkpoints from Hugging Face."""
from __future__ import annotations

import argparse
import os

from huggingface_hub import snapshot_download


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Download OSS checkpoints")
    p.add_argument(
        "--repo",
        default="openai/oss-120b",
        help="Model repository on Hugging Face",
    )
    p.add_argument("--out", default="oss-120b", help="Destination directory")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    path = snapshot_download(
        args.repo, local_dir=args.out, local_dir_use_symlinks=False
    )
    shards = [f for f in os.listdir(path) if f.endswith(".safetensors")]
    if not shards:
        raise SystemExit("No weight shards downloaded; check repository name")
    print(f"Downloaded {len(shards)} weight shards to {path}")


if __name__ == "__main__":
    main()
