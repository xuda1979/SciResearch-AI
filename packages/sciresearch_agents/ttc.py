from typing import List, Dict, Any
from .protocols import Strategy

class TTC(Strategy):
    def plan(self, problem: str) -> List[str]:
        return [f"step 1 for {problem}", f"step 2 for {problem}"]

    def expand(self, step: str) -> List[str]:
        return [f"expansion 1 for {step}", f"expansion 2 for {step}"]

    def score(self, step: str, expansions: List[str]) -> Dict[str, float]:
        return {expansion: i * 0.1 for i, expansion in enumerate(expansions)}

    def select(self, scores: Dict[str, float]) -> str:
        if not scores:
            return ""
        return max(scores, key=lambda k: scores[k])
