"""
Answer Futures Market (AFM) example.

This script simulates routing a query between a small and a large model based
on confidence thresholds and cost.
"""

try:
    from sciresearch_ai import __version__ as _version  # type: ignore
except Exception:
    _version = "unknown"

from typing import Tuple


def small_model(question: str) -> Tuple[str, float, float]:
    """Return answer, confidence, and cost for a small model."""
    answer = "42"
    confidence = 0.6
    cost = 1.0
    return answer, confidence, cost


def large_model(question: str) -> Tuple[str, float, float]:
    """Return answer, confidence, and cost for a large model."""
    answer = "42"
    confidence = 0.95
    cost = 5.0
    return answer, confidence, cost


def router(question: str, threshold: float = 0.8) -> Tuple[str, float, str]:
    """
    Route question based on confidence threshold.

    Args:
        question (str): The question to answer.
        threshold (float): Confidence threshold for using the small model.

    Returns:
        Tuple[str, float, str]: The answer, confidence, and model name used.
    """
    ans_s, conf_s, _ = small_model(question)
    if conf_s >= threshold:
        return ans_s, conf_s, "small_model"
    ans_l, conf_l, _ = large_model(question)
    return ans_l, conf_l, "large_model"


def main() -> None:
    """Demonstrate answer futures market routing."""
    question = "What is the answer to life?"
    answer, conf, model_used = router(question)
    print("sciresearch_ai version:", _version)
    print(f"Used {model_used} with confidence {conf}. Answer: {answer}")


if __name__ == "__main__":
    main()