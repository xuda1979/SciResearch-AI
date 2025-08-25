"""
Deterministic Shadow‑OS for Agents (DSOS) example.

This script demonstrates creating an intention log, simulating actions, and
requiring approval before committing.
"""

try:
    from sciresearch_ai import __version__ as _version  # type: ignore
except Exception:
    _version = "unknown"

from typing import List, Dict, Any


def create_intention_log() -> List[Dict[str, Any]]:
    """Return an example list of planned actions for the agent."""
    return [
        {"action": "write_file", "path": "output.txt", "content": "Hello"},
        {"action": "click", "selector": "button#submit"},
    ]


def simulate_actions(log: List[Dict[str, Any]]) -> List[str]:
    """Simulate the actions and return a summary without side effects."""
    diffs: List[str] = []
    for step in log:
        if step["action"] == "write_file":
            diffs.append(f"Would write to {step['path']}")
        elif step["action"] == "click":
            diffs.append(f"Would click on {step['selector']}")
    return diffs


def commit_actions(log: List[Dict[str, Any]], approved: bool) -> None:
    """Execute the actions if approved."""
    if not approved:
        print("Actions not approved. Aborting.")
        return
    print("Executing actions...")
    for step in log:
        print(f"Executing {step}")
    print("Done.")


def main() -> None:
    """Demonstrate deterministic shadow‑OS."""
    log = create_intention_log()
    diff = simulate_actions(log)
    print("sciresearch_ai version:", _version)
    print("Proposed diff:")
    for line in diff:
        print(" -", line)
    commit_actions(log, approved=True)  # In practice, approval would come from a verifier


if __name__ == "__main__":
    main()