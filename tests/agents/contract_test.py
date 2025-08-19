import pytest

from packages.sciresearch_agents.registry import STRATEGIES, get_strategy


@pytest.mark.parametrize("strategy_name", STRATEGIES.keys())
def test_strategy_contract(strategy_name):
    """
    Tests that all strategies adhere to the Strategy protocol contract.
    """
    strategy = get_strategy(strategy_name)
    problem = "test problem"

    # Test plan
    plan = strategy.plan(problem)
    assert isinstance(plan, list)
    assert all(isinstance(step, str) for step in plan)
    assert len(plan) > 0, "Plan should not be empty"

    # Test expand
    step = plan[0]
    expansions = strategy.expand(step)
    assert isinstance(expansions, list)
    assert all(isinstance(expansion, str) for expansion in expansions)
    assert len(expansions) > 0, "Expansions should not be empty"

    # Test score
    scores = strategy.score(step, expansions)
    assert isinstance(scores, dict)
    assert all(isinstance(k, str) for k in scores.keys())
    assert all(isinstance(v, float) for v in scores.values())
    assert set(scores.keys()) == set(expansions), "Scores must be for all expansions"

    # Test select
    selected = strategy.select(scores)
    assert isinstance(selected, str)
    assert (
        selected in expansions
    ), "Selected expansion must be one of the original expansions"
