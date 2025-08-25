import re


def _escape_latex(text: str) -> str:
    """Escapes special LaTeX characters in a string."""
    chars = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\^{}",
        "\\": r"\textbackslash{}",
    }
    regex = re.compile("|".join(map(re.escape, chars.keys())))
    return regex.sub(lambda match: chars[match.group(0)], text)


def _escape_non_math(text: str) -> str:
    """Escape LaTeX outside math mode.

    Any segments wrapped in ``$...$`` are returned verbatim so that
    mathematical macros (e.g. ``\alpha``) are preserved.  Text outside
    math mode still has the usual special characters escaped via
    :func:`_escape_latex`.
    """
    parts: list[str] = []
    last = 0
    for match in re.finditer(r"\$(.+?)\$", text, re.DOTALL):
        start, end = match.span()
        parts.append(_escape_latex(text[last:start]))
        parts.append(match.group(0))  # keep math segment as-is
        last = end
    parts.append(_escape_latex(text[last:]))
    return "".join(parts)


def _format_code(code: str) -> str:
    """Formats a code block for LaTeX."""
    return f"\\begin{{verbatim}}\n{code.strip()}\n\\end{{verbatim}}"


def parse_response(raw_text: str) -> str:
    """Parses a raw response from the language model and formats it for LaTeX.

    This function identifies code blocks (enclosed in ```) and wraps them in a
    verbatim environment, while escaping special LaTeX characters in the
    surrounding text.

    Args:
        raw_text: The raw string from the language model.

    Returns:
        A LaTeX-formatted string.
    """
    parts = []
    last_end = 0
    # Regex to find code blocks, optionally with a language hint
    for match in re.finditer(r"```(\w+)?\n(.*?)```", raw_text, re.DOTALL):
        start, end = match.span()
        # Append the text before the code block, escaping only outside math
        parts.append(_escape_non_math(raw_text[last_end:start]))
        # Append the formatted code block
        parts.append(_format_code(match.group(2)))
        last_end = end

    # Append any remaining text after the last code block, with escaping
    parts.append(_escape_non_math(raw_text[last_end:]))

    return "".join(parts)
