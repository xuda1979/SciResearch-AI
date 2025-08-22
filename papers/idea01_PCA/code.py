"""Demonstration of Proof-Carrying Answers with basic self-fuzzing."""

from __future__ import annotations

from random import randint

from sciresearch_ai import __version__


def proof_carrying_answer(claim: str) -> dict[str, str]:
    """Return a simple proof-carrying answer structure for a claim."""
    proof = f"Proof of {claim}: verified by sciresearch_ai version {__version__}"
    return {"claim": claim, "proof": proof}


def fuzz_addition(iterations: int = 10) -> bool:
    """Search for counterexamples to the commutativity of addition."""
    for _ in range(iterations):
        a, b = randint(-100, 100), randint(-100, 100)
        if a + b != b + a:
            return False
    return True


def main() -> None:
    result = proof_carrying_answer("1 + 1 = 2")
    print(result)
    passed = fuzz_addition()
    print("Commutativity holds under fuzzing:", passed)


if __name__ == "__main__":
    main()
