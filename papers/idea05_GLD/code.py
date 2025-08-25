"""
Global‑then‑Local Decoding (GLD) example.

This script constructs a simple global outline and then fills each section with
placeholder text.
"""

try:
    from sciresearch_ai import __version__ as _version  # type: ignore
except Exception:
    _version = "unknown"


def create_plan() -> list[str]:
    """Return a simple list representing a global plan."""
    return ["Introduction", "Background", "Method", "Conclusion"]


def fill_sections(plan: list[str]) -> dict[str, str]:
    """Fill sections according to the plan with placeholder text."""
    sections: dict[str, str] = {}
    for section in plan:
        sections[section] = f"This is the {section.lower()} section filled according to the plan."
    return sections


def main() -> None:
    """Demonstrate global‑then‑local decoding."""
    plan = create_plan()
    filled = fill_sections(plan)
    print(f"sciresearch_ai version: {_version}")
    print("Plan:", plan)
    for sec, content in filled.items():
        print(f"{sec}: {content}")


if __name__ == "__main__":
    main()