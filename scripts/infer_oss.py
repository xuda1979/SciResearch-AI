#!/usr/bin/env python
"""Simple text generation script using the OSS 120B wrapper."""
from __future__ import annotations

import argparse
from sciresearch_ai.providers import OssProvider


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate text with OSS 120B")
    p.add_argument("prompt", help="Input prompt text")
    p.add_argument("--model", default=None, help="Optional model name or path")
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
    p.add_argument("--enable-browser", action="store_true", help="Allow web search tool")
    p.add_argument("--enable-python", action="store_true", help="Allow sandboxed Python tool")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    provider = OssProvider(
        checkpoint=args.model,
        device=args.device,
        enable_browser=args.enable_browser,
        enable_python=args.enable_python,
    )
    text = provider.generate(args.prompt, max_new_tokens=args.max_new_tokens)[0]
    print(text)


if __name__ == "__main__":
    main()
