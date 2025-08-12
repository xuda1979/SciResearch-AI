#!/usr/bin/env python
"""Simple text generation script using the OSS 120B wrapper."""
from __future__ import annotations

import argparse
from sciresearch_ai.models.oss_120b import load_model


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate text with OSS 120B")
    p.add_argument("prompt", help="Input prompt text")
    p.add_argument("--model", default=None, help="Optional model name or path")
    p.add_argument("--max-new-tokens", type=int, default=50, help="Number of tokens to generate")
    p.add_argument("--npu", action="store_true", help="Use Ascend NPU for inference")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    model, tokenizer = load_model(args.model, device="npu" if args.npu else None)
    inputs = tokenizer(args.prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=args.max_new_tokens)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(text)


if __name__ == "__main__":
    main()
