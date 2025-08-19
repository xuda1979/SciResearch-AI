from __future__ import annotations

from sympy import Eq, simplify, sympify


def check_symbolic_equality(expr1: str, expr2: str) -> bool:
    try:
        e1 = sympify(expr1)
        e2 = sympify(expr2)
        return simplify(e1 - e2) == 0
    except Exception:
        return False
