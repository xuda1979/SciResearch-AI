"""
Knowledge Fossilization via Micro‑Theorems example.

This script defines a simple micro‑theorem as a Python function along with an
associated unit test.
"""

try:
    from sciresearch_ai import __version__ as _version  # type: ignore
except Exception:
    _version = "unknown"


def theorem_celsius_to_fahrenheit(celsius: float) -> float:
    """
    Convert Celsius to Fahrenheit.

    Args:
        celsius (float): Temperature in degrees Celsius.

    Returns:
        float: Temperature in degrees Fahrenheit.
    """
    return celsius * 9.0 / 5.0 + 32.0


def test_celsius_to_fahrenheit(celsius: float, expected_f: float, tolerance: float = 1e-6) -> bool:
    """
    Test the Celsius‑to‑Fahrenheit micro‑theorem.

    Args:
        celsius (float): Temperature in degrees Celsius.
        expected_f (float): Expected Fahrenheit value.
        tolerance (float): Acceptable difference.

    Returns:
        bool: True if the difference is within tolerance, False otherwise.
    """
    return abs(theorem_celsius_to_fahrenheit(celsius) - expected_f) < tolerance


def main() -> None:
    """Demonstrate the micro‑theorem and its test."""
    print(f"Using sciresearch_ai version {_version}")
    c_val = 100.0
    f_val = theorem_celsius_to_fahrenheit(c_val)
    print(f"Micro‑theorem: {c_val} Celsius = {f_val} Fahrenheit")
    assert test_celsius_to_fahrenheit(c_val, 212.0), "Micro‑theorem test failed!"
    print("Test passed: 100 C equals 212 F according to the micro‑theorem.")


if __name__ == "__main__":
    main()