from typing import Any, Dict, List, Protocol

from .types import Candidate, Decision, Message, Plan, RunResult


class ToolSpec(Protocol):
    name: str
    description: str
    parameters: Dict[str, Any]


class ToolCall(Protocol):
    tool_name: str
    arguments: Dict[str, Any]


class ToolResult(Protocol):
    tool_name: str
    result: Any


class Tool(Protocol):
    def get_spec(self) -> ToolSpec: ...

    def execute(self, call: ToolCall) -> ToolResult: ...


class Provider(Protocol):
    def chat(self, messages: List[Message]) -> Message: ...


class Strategy(Protocol):
    def plan(self, goal: str) -> Plan: ...

    def decide(self, candidates: List[Candidate]) -> Decision: ...


class ProjectFS(Protocol):
    def read(self, path: str) -> str: ...

    def write(self, path: str, content: str) -> None: ...

    def list(self, path: str) -> List[str]: ...


class PaperWriter(Protocol):
    def write_paper(self, research_summary: str) -> str: ...


class ResearchLoop(Protocol):
    def run(self) -> RunResult: ...
