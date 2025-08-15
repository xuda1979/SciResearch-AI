#!/usr/bin/env python
"""Minimal PPO fine-tuning loop for the OSS 120B model."""
from __future__ import annotations

import argparse
import os

from datasets import load_dataset
from trl import PPOConfig, PPOTrainer

from sciresearch_ai.config import RLConfig
from sciresearch_ai.models.oss_120b import load_model


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="RL fine-tuning for OSS 120B")
    p.add_argument("--data", required=True, help="Path to JSONL dataset")
    p.add_argument(
        "--output",
        default="checkpoints/oss-120b-rl",
        help="Where to save fine-tuned weights",
    )
    p.add_argument("--model", default=None, help="Optional model name or path")
    p.add_argument(
        "--device",
        choices=["cpu", "cuda", "npu"],
        default=None,
        help="Device for training",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = RLConfig()
    model, tokenizer = load_model(args.model, device=args.device)
    ds = load_dataset("json", data_files=args.data)["train"]

    ppo_config = PPOConfig(
        model_name=args.model or "openai/oss-120b",
        learning_rate=cfg.learning_rate,
        batch_size=cfg.batch_size,
        mini_batch_size=cfg.mini_batch_size,
        gradient_accumulation_steps=cfg.gradient_accumulation_steps,
        optimize_cuda_cache=True,
    )
    trainer = PPOTrainer(ppo_config, model, tokenizer, dataset=ds)
    trainer.train()

    os.makedirs(args.output, exist_ok=True)
    model.save_pretrained(args.output)
    tokenizer.save_pretrained(args.output)


if __name__ == "__main__":
    main()
