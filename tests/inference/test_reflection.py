import sciresearch_ai.inference.reflection as reflection


def test_critique_and_revise_runs_three_passes():
    prompts = []

    def mock_gen(prompt: str, n: int):
        prompts.append(prompt)
        return [f"reply {len(prompts)}"]

    result = reflection.critique_and_revise(mock_gen, draft="Start")
    assert len(result["critiques"]) == 3
    assert "CHECKLIST" in prompts[0]
    assert result["final"] == "reply 6"
