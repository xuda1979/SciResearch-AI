from typing import Any

from sympy import simplify, sympify


class SymEqTool:
    """A tool for checking symbolic equality of two expressions."""

    @property
    def name(self) -> str:
        return "symbolic_equality"

    @property
    def description(self) -> str:
        return "Checks if two mathematical expressions are symbolically equal."

    async def __call__(self, expr1: str, expr2: str) -> bool:
        """
        Check if two expressions are symbolically equal.
        Returns True if they are, False otherwise.
        """
        try:
            e1 = sympify(expr1)
            e2 = sympify(expr2)
            return simplify(e1 - e2) == 0
        except Exception:
            return False
