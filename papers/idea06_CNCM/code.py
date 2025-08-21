"""
Example code for Counterparty Models with Verifiable Non-Collusion (CNCM).
This script simulates an advocate, a skeptic, and a judge playing roles to verify answers.
"""
from sciresearch_ai import __version__

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
    question = "What is the answer to everything?"
    a_answer = advocate(question)
    s_answer = skeptic(question)
    final = judge(a_answer, s_answer)
    print("sciresearch_ai version:", __version__)
    print(final)

if __name__ == "__main__":
    main()
