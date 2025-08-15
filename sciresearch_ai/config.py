from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RunConfig:
    model: str = "gpt-5-chat-latest"
    max_iterations: int = 10
    samples_per_query: int = 5  # test-time compute for self-consistency
    time_budget_sec: int = 1800
    parallel_workers: int = 2
    devices: List[str] = field(default_factory=list)  # e.g., ["cuda:0"]
    reasoning_effort: str = "high"  # low | medium | high
    temperature: float = 0.2
    top_p: float = 0.9
    max_output_tokens: int = 2000
    budget_usd: Optional[float] = None  # soft budget tracker (not enforced by API)
    interactive: bool = True
    enable_code_interpreter: bool = False  # GPT-5 tool: server-side code interpreter


@dataclass
class RLConfig:
    """Hyperparameters for reinforcement learning fine-tuning."""

    learning_rate: float = 1e-5
    batch_size: int = 4
    mini_batch_size: int = 1
    gradient_accumulation_steps: int = 1
    epochs: int = 1
