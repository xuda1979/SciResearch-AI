"""
Entropy‑Thermostat Decoding (ETD) example.

This script generates random probability distributions, computes their
entropies, and adjusts a temperature parameter toward a target entropy.
"""

try:
    from sciresearch_ai import __version__ as _version  # type: ignore
except Exception:
    _version = "unknown"

import random
import math
from typing import List, Iterable


def entropy(probs: Iterable[float]) -> float:
    """Compute the entropy of a probability distribution."""
    return -sum(p * math.log(p + 1e-12) for p in probs)


def generate_prob_sequences(num_steps: int = 5, vocab_size: int = 5) -> List[List[float]]:
    """
    Generate a sequence of random probability distributions.

    Args:
        num_steps (int): Number of timesteps.
        vocab_size (int): Size of the vocabulary.

    Returns:
        List[List[float]]: A list of probability distributions.
    """
    sequences: List[List[float]] = []
    for _ in range(num_steps):
        values = [random.random() for _ in range(vocab_size)]
        total = sum(values)
        probs = [v / total for v in values]
        sequences.append(probs)
    return sequences


def thermostat_decode(prob_sequences: List[List[float]], target_entropy: float = 1.0) -> float:
    """
    Adjust temperature based on entropy across a sequence of probability distributions.

    Args:
        prob_sequences (List[List[float]]): Sequence of probability distributions.
        target_entropy (float): Target entropy value.

    Returns:
        float: The final temperature after processing all distributions.
    """
    temperature = 1.0
    for step, probs in enumerate(prob_sequences, 1):
        ent = entropy(probs)
        if ent > target_entropy:
            temperature *= 0.9  # Decrease temperature -> sharper distribution
        else:
            temperature *= 1.1  # Increase temperature -> smoother distribution
        print(f"Step {step}: entropy={ent:.3f}, temperature={temperature:.3f}")
    return temperature


def main() -> None:
    """Generate example probabilities and run the entropy‑thermostat decoder."""
    print(f"Using sciresearch_ai version {_version}")
    prob_sequences = generate_prob_sequences(num_steps=8, vocab_size=6)
    final_temp = thermostat_decode(prob_sequences, target_entropy=1.5)
    print(f"Final temperature: {final_temp:.3f}")


if __name__ == "__main__":
    main()