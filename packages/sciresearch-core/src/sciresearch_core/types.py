from dataclasses import dataclass
from typing import Any, List


@dataclass
class Message:
    role: str
    content: str


@dataclass
class Plan:
    steps: List[str]


@dataclass
class Candidate:
    id: str
    data: Any


@dataclass
class Score:
    value: float
    reasoning: str


@dataclass
class Decision:
    candidate: Candidate
    score: Score
    reasoning: str


@dataclass
class RunResult:
    success: bool
    output: Any
