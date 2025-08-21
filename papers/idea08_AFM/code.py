"""
Example code for Answer Futures Market (AFM).
This script simulates a small and a large model bidding their confidence and cost.
"""
from sciresearch_ai import __version__

def small_model(question: str):
    """Return answer, confidence, and cost for a small model."""
    answer = "42"
    confidence = 0.6
    cost = 1
    return answer, confidence, cost

def large_model(question: str):
    """Return answer, confidence, and cost for a large model."""
    answer = "42"
    confidence = 0.95
    cost = 5
    return answer, confidence, cost

def router(question: str, threshold: float = 0.8):
    """Route question based on confidence threshold."""
    ans_s, conf_s, cost_s = small_model(question)
    if conf_s >= threshold:
        return ans_s, conf_s, "small_model"
    ans_l, conf_l, cost_l = large_model(question)
    return ans_l, conf_l, "large_model"

def main() -> None:
    question = "What is the answer to life?"
    answer, conf, model_used = router(question)
    print("sciresearch_ai version:", __version__)
    print(f"Used {model_used} with confidence {conf}. Answer: {answer}")

if __name__ == "__main__":
    main()
