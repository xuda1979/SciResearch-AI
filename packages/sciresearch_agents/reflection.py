from typing import Any, Dict, List

from .protocols import Strategy


class Reflection(Strategy):
    def plan(self, problem: str) -> List[str]:
        return [f"reflection step 1 for {problem}", f"reflection step 2 for {problem}"]

    def expand(self, step: str) -> List[str]:
        return [
            f"reflection expansion 1 for {step}",
            f"reflection expansion 2 for {step}",
        ]

    def score(self, step: str, expansions: List[str]) -> Dict[str, float]:
        # Reflection might involve self-correction, so scores could be adjusted
        return {expansion: 0.8 for expansion in expansions}

    def select(self, scores: Dict[str, float]) -> str:
        if not scores:
            return ""
        return max(scores, key=lambda k: scores[k])
