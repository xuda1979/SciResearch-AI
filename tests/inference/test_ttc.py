import sciresearch_ai.inference.ttc as ttc


def test_tree_of_thoughts_selects_best_path():
    expansions = {
        "root": ["A", "B"],
        "root\nA": ["A1", "A2"],
        "root\nB": ["B1", "B2"],
    }
    scores = {
        "root\nA": 1,
        "root\nB": 2,
        "root\nA\nA1": 3,
        "root\nA\nA2": 4,
        "root\nB\nB1": 5,
        "root\nB\nB2": 6,
    }

    def provider(state: str, n: int):
        # ignore n to expose all candidates for scoring
        return expansions.get(state, [])

    def scorer(state: str) -> float:
        return scores.get(state, 0)

    result = ttc.tree_of_thoughts(provider, "root", depth=2, breadth=1, scorer=scorer)
    assert result["path"] == ["B", "B2"]
    assert result["best"].endswith("B2")
