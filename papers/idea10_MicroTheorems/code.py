"""
Example code for idea10 (Knowledge Fossilization via Micro-Theorems).
This script defines a simple "micro-theorem" as a Python function and an associated test
that checks a factual relationship. In practice, a library of such micro-theorems with
unit tests would help a language model retain and verify critical domain knowledge.
"""

from sciresearch_ai import __version__

# A simple micro-theorem: convert Celsius to Fahrenheit
# The theorem expresses the relationship between Celsius and Fahrenheit scales.
def theorem_celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 9.0 / 5.0 + 32.0

# A test function for the micro-theorem
# It returns True if the conversion matches the expected Fahrenheit value within a small tolerance
def test_celsius_to_fahrenheit(celsius: float, expected_f: float, tolerance: float = 1e-6) -> bool:
    return abs(theorem_celsius_to_fahrenheit(celsius) - expected_f) < tolerance

if __name__ == "__main__":
    print(f"Using sciresearch_ai version {__version__}")
    # Demonstrate the theorem and test
    c_val = 100.0
    f_val = theorem_celsius_to_fahrenheit(c_val)
    print(f"Micro-theorem: {c_val} Celsius = {f_val} Fahrenheit")
    # Verify with the test
    assert test_celsius_to_fahrenheit(c_val, 212.0), "Micro-theorem test failed!"
    print("Test passed: 100 C equals 212 F according to the micro-theorem.")
