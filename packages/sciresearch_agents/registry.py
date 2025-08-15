from typing import Dict, Type
from .protocols import Strategy
from .ttc import TTC
from .bad import BAD
from .debate import Debate
from .reflection import Reflection

STRATEGIES: Dict[str, Type[Strategy]] = {
    "ttc": TTC,
    "bad": BAD,
    "debate": Debate,
    "reflection": Reflection,
}

def get_strategy(name: str) -> Strategy:
    strategy_class = STRATEGIES.get(name)
    if not strategy_class:
        raise ValueError(f"Unknown strategy: {name}")
    return strategy_class()
