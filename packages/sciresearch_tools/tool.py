from typing import Protocol, Any, Awaitable

class Tool(Protocol):
    """A protocol for tools that can be called by the agent."""

    @property
    def name(self) -> str:
        """The name of the tool."""
        ...

    @property
    def description(self) -> str:
        """A description of the tool."""
        ...

    def __call__(self, *args: Any, **kwargs: Any) -> Awaitable[Any]:
        """Call the tool."""
        ...
