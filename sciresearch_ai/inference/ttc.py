from __future__ import annotations

import math
from typing import Any, Callable, Dict, List, Tuple

# --- Test-Time Compute (TTC) strategies ---
# Self-consistency / Best-of-N with majority vote + simple scoring hooks.


def self_consistency(
    provider_generate: Callable[[str, int], List[str]],
    prompt: str,
    n: int,
    scorer: Callable[[str], float] | None = None,
) -> Dict[str, Any]:
    samples = provider_generate(prompt, n)
    if not samples:
        return {"best": "", "samples": []}
    if scorer:
        scores = [scorer(s) for s in samples]
        best_idx = max(range(len(samples)), key=lambda i: scores[i])
    else:
        # majority vote by exact-string mode (toy baseline)
        counts = {}
        for s in samples:
            counts[s] = counts.get(s, 0) + 1
        best_idx = max(range(len(samples)), key=lambda i: counts[samples[i]])
        scores = [counts[s] for s in samples]
    return {"best": samples[best_idx], "samples": samples, "scores": scores}


def budgeted_adaptive_deliberation(
    provider_generate: Callable[[str, int], List[str]],
    prompt: str,
    total_budget: int,
    batch_size: int = 2,
    scorer: Callable[[str], float] | None = None,
    early_stop_margin: float = 0.15,
) -> Dict[str, Any]:
    # A novel-ish TTC variant: allocate samples in rounds; stop early when the
    # running best is sufficiently ahead by a margin. Otherwise, keep sampling.
    all_samples: List[str] = []
    all_scores: List[float] = []
    spent = 0
    best = None
    best_score = -math.inf
    while spent < total_budget:
        take = min(batch_size, total_budget - spent)
        new_samples = provider_generate(prompt, take)
        all_samples.extend(new_samples)
        if scorer:
            new_scores = [scorer(s) for s in new_samples]
        else:
            new_scores = [0.0 for _ in new_samples]  # neutral if no scorer
        all_scores.extend(new_scores)
        spent += take
        # check margin-early-stop
        b_idx = max(
            range(len(all_samples)), key=lambda i: all_scores[i] if all_scores else 0.0
        )
        b_score = all_scores[b_idx] if all_scores else 0.0
        if b_score - best_score > early_stop_margin:
            best = all_samples[b_idx]
            best_score = b_score
        # if the best is sufficiently ahead of the current average, stop early
        avg = sum(all_scores) / max(1, len(all_scores))
        if best_score >= avg + early_stop_margin:
            break
    if best is None and all_samples:
        best = all_samples[0]
    return {"best": best or "", "samples": all_samples, "scores": all_scores}


def tree_of_thoughts(
    provider_generate: Callable[[str, int], List[str]],
    prompt: str,
    depth: int,
    breadth: int,
    scorer: Callable[[str], float] | None = None,
) -> Dict[str, Any]:
    """Simple breadth-first Tree-of-Thoughts search.

    Args:
        provider_generate: function that expands a state into ``breadth`` thoughts.
        prompt: initial state to expand from.
        depth: number of expansion rounds.
        breadth: beam width; number of states kept per level.
        scorer: optional heuristic to rank states. Higher is better.

    Returns:
        Mapping with the best final state and the path of thoughts leading to it.
    """

    frontier: List[Tuple[str, List[str]]] = [(prompt, [])]
    for _ in range(depth):
        candidates: List[Tuple[str, List[str]]] = []
        for state, path in frontier:
            thoughts = provider_generate(state, breadth)
            for t in thoughts:
                new_state = f"{state}\n{t}"
                candidates.append((new_state, path + [t]))
        if not candidates:
            break
        if scorer:
            candidates.sort(key=lambda n: scorer(n[0]), reverse=True)
        frontier = candidates[:breadth]
    best_state, best_path = frontier[0] if frontier else ("", [])
    return {"best": best_state, "path": best_path}
