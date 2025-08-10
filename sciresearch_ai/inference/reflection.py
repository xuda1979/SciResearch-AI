from __future__ import annotations
from typing import Callable, Dict, Any, List

CRITIC_SYS = "You are a meticulous reviewer. Identify errors, missing citations, and unclear logic. Propose concrete fixes."

def critique_and_revise(
    provider_generate: Callable[[str, int], List[str]],
    draft: str,
    passes: int = 2,
) -> Dict[str, Any]:
    history: List[str] = []
    current = draft
    for i in range(passes):
        critique = provider_generate(f"{CRITIC_SYS}\nPlease review the following draft and critique it:\n{current}", 1)[0]
        history.append(critique)
        revised = provider_generate(
            "Revise the draft to resolve the above critique. Return only the revised text.\n"
            f"CRITIQUE:\n{critique}\nDRAFT:\n{current}", 1
        )[0]
        current = revised
    return {"final": current, "critiques": history}
