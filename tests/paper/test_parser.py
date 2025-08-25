import unittest
from sciresearch_ai.paper.parser import parse_response


class TestParser(unittest.TestCase):
    def test_parse_response(self):
        raw_text = """This is a test response.
It contains some special characters like & % $ # _ { }.
Also, here is a code block:
```python
def main():
    print("Hello, world!")
```
And some final text.
"""
        expected_output = r"""This is a test response.
It contains some special characters like \& \% \$ \# \_ \{ \}.
Also, here is a code block:
\begin{verbatim}
def main():
    print("Hello, world!")
\end{verbatim}
And some final text.
"""
        self.assertEqual(parse_response(raw_text).strip(), expected_output.strip())

    def test_escape_latex(self):
        from sciresearch_ai.paper.parser import _escape_latex
        self.assertEqual(_escape_latex("a&b"), r"a\&b")
        self.assertEqual(_escape_latex("{a_b}"), r"\{a\_b\}")

    def test_math_is_preserved(self):
        raw = "The error term $\\varepsilon$ is small."
        self.assertEqual(parse_response(raw).strip(), raw)


if __name__ == "__main__":
    unittest.main()
