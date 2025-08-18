import pytest

from packages.sciresearch_tools.sym_eq_tool import SymEqTool


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expr1, expr2, expected",
    [
        ("x + 1", "1 + x", True),
        ("x**2 - 1", "(x - 1)*(x + 1)", True),
        ("a*b", "b*a", True),
        ("x + 1", "x + 2", False),
        ("x*y", "x*z", False),
    ],
)
async def test_sym_eq_tool_positive_cases(expr1, expr2, expected):
    """Test that the tool correctly identifies equal and unequal expressions."""
    tool = SymEqTool()
    output = await tool(expr1, expr2)
    assert output == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expr1, expr2",
    [
        ("x + ", "1 + x"),
        ("x**2 - 1", "(x - 1)*("),
    ],
)
async def test_sym_eq_tool_invalid_expressions(expr1, expr2):
    """Test that the tool handles invalid expressions gracefully."""
    tool = SymEqTool()
    output = await tool(expr1, expr2)
    assert output is False
