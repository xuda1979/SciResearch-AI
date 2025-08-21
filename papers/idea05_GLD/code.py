"""
Example of Global-then-Local Decoding (GLD).

This script constructs a simple global plan and then fills sections
according to the plan. In practice, the plan could be produced by a
language model and validated before filling.
"""

from sciresearch_ai import __version__


def create_plan():
    """Return a simple list representing a global plan."""
    # Example plan: list of section titles
    return ["Introduction", "Background", "Method", "Conclusion"]


def fill_sections(plan):
    """Fill sections according to the plan with placeholder text."""
    sections = {}
    for section in plan:
        sections[section] = (
            f"This is the {section.lower()} section filled according to the plan."
        )
    return sections


def main():
    plan = create_plan()
    filled = fill_sections(plan)
    print(f"sciresearch_ai version: {__version__}")
    print("Plan:", plan)
    for sec, content in filled.items():
        print(f"{sec}: {content}")


if __name__ == "__main__":
    main()
