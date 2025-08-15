from __future__ import annotations

import random
import time
from typing import List


class MockProvider:
    name = "mock"

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def generate(self, prompt: str, n: int = 1, **gen_kwargs) -> List[str]:
        # Deterministic-ish canned responses for testing
        random.seed(hash(prompt) % (2**32))
        out = []
        for i in range(n):
            out.append(
                f"[MOCK-{i}] Response for: {prompt[:60]}...\nKey points: hypothesis -> small experiment -> result -> write."
            )
        time.sleep(0.01)
        return out
