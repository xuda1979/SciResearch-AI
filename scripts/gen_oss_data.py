#!/usr/bin/env python
"""Generate JSONL training data using the OSS provider."""
from __future__ import annotations

import argparse
from typing import List

from sciresearch_ai.data.ingestion import ingest_records, normalize_record
from sciresearch_ai.providers import OssProvider


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate dataset with OSS model")
    p.add_argument("--prompt", help="Prompt text to sample from")
    p.add_argument("--samples", type=int, default=1, help="Number of samples to generate")
    p.add_argument("--out", required=True, help="Output JSONL path")
    p.add_argument("--model", default=None, help="Optional model name or path")
    p.add_argument("--enable-browser", action="store_true", help="Allow web search tool")
    p.add_argument("--enable-python", action="store_true", help="Allow sandboxed Python tool")
    p.add_argument(
        "--device",
        choices=["cpu", "cuda", "npu"],
        default=None,
        help="Device for running the model",
    )
    p.add_argument(
        "--max-new-tokens",
        type=int,
        default=None,
        help="Maximum number of tokens to generate",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    provider = OssProvider(
        checkpoint=args.model,
        device=args.device,
        enable_browser=args.enable_browser,
        enable_python=args.enable_python,
    )
    records: List = []
    for _ in range(args.samples):
        resp = provider.generate(args.prompt, max_new_tokens=args.max_new_tokens)[0]
        records.append(
            normalize_record("oss-120b", args.prompt, resp)
        )
    ingest_records(records, args.out)
    print(f"Appended {len(records)} records to {args.out}")


if __name__ == "__main__":
    main()
