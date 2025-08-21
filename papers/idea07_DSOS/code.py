"""
Example code for Deterministic Shadow-OS for Agents (DSOS).
This script demonstrates creating an intention log, simulating execution,
and requiring approval before performing real actions.
"""
from sciresearch_ai import __version__

def create_intention_log():
    """Return an example list of actions for the agent."""
    return [
        {"action": "write_file", "path": "output.txt", "content": "Hello"},
        {"action": "click", "selector": "button#submit"},
    ]

def simulate_actions(log):
    """Simulate the actions and return a diff summary."""
    diffs = []
    for step in log:
        if step["action"] == "write_file":
            diffs.append(f"Would write to {step['path']}")
        elif step["action"] == "click":
            diffs.append(f"Would click on {step['selector']}")
    return diffs

def commit_actions(log, approved: bool) -> None:
    """Execute the actions if approved."""
    if not approved:
        print("Actions not approved. Aborting.")
        return
    print("Executing actions...")
    for step in log:
        print(f"Executing {step}")
    print("Done.")

def main() -> None:
    log = create_intention_log()
    diff = simulate_actions(log)
    print("sciresearch_ai version:", __version__)
    print("Proposed diff:")
    for line in diff:
        print(" -", line)
    # In practice, approval would come from a human or verifier
    commit_actions(log, approved=True)

if __name__ == "__main__":
    main()
