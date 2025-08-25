"""
Counterparty Models with Verifiable Non‑Collusion (CNCM) example.

This script simulates an advocate, a skeptic, and a judge to aggregate multiple
viewpoints.
"""

try:
    from sciresearch_ai import __version__ as _version  # type: ignore
except Exception:
    _version = "unknown"


def advocate(question: str) -> str:
    """Propose an answer for a given question."""
    return f"Answer to {question}: 42"


def skeptic(question: str) -> str:
    """Provide a counterargument or alternative perspective."""
    return f"Skeptic disagrees with the answer to '{question}' and proposes an alternative."


def judge(adv_answer: str, skep_response: str) -> str:
    """Aggregate the advocate and skeptic responses."""
    if adv_answer and skep_response:
        return (
            f"Final decision: Both perspectives considered. Advocate said: '{adv_answer}'. "
            f"Skeptic said: '{skep_response}'."
        )
    return adv_answer or skep_response


def main() -> None:
    """Demonstrate the CNCM protocol."""
    question = "What is the answer to everything?"
    a_answer = advocate(question)
    s_answer = skeptic(question)
    final = judge(a_answer, s_answer)
    print("sciresearch_ai version:", _version)
    print(final)


if __name__ == "__main__":
    main()