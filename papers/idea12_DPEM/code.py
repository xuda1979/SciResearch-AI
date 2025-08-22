from sciresearch_ai import __version__

class DPEMStore:
    """A simple differentially private, revocable in-memory store with TTL."""

    def __init__(self, epsilon_budget: float):
        self.epsilon_budget = epsilon_budget
        self.store = []  # list of dicts with keys: value, eps, ttl, rev

    def add(self, value: str, epsilon: float, ttl: int, rev_id: str) -> None:
        """Add an entry if it fits within the remaining DP budget."""
        if epsilon > self.epsilon_budget:
            raise ValueError("Value requires too much epsilon budget remaining")
        # deduct from budget
        self.epsilon_budget -= epsilon
        self.store.append({"value": value, "eps": epsilon, "ttl": ttl, "rev": rev_id})

    def retrieve(self) -> list:
        """Retrieve entries that are still valid (ttl > 0)."""
        valid_items = []
        for item in self.store:
            if item["ttl"] > 0:
                valid_items.append(item["value"])
        return valid_items

    def tick(self) -> None:
        """Advance time by one unit, decrementing TTLs."""
        for item in self.store:
            if item["ttl"] > 0:
                item["ttl"] -= 1

    def revoke(self, rev_id: str) -> None:
        """Remove all entries matching the revocation id."""
        self.store = [item for item in self.store if item["rev"] != rev_id]


if __name__ == "__main__":
    # Example usage
    mem = DPEMStore(epsilon_budget=1.0)
    mem.add("First sensitive fact", epsilon=0.4, ttl=5, rev_id="abc123")
    mem.add("Second fact", epsilon=0.3, ttl=3, rev_id="xyz789")
    print("Initial retrieval:", mem.retrieve())
    # simulate time passing
    mem.tick()
    mem.tick()
    print("After ticking twice:", mem.retrieve())
    # revoke the first fact
    mem.revoke("abc123")
    print("After revocation:", mem.retrieve())
    print("sciresearch_ai version:", __version__)
