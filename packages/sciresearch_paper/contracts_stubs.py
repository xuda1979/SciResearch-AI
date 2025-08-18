from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Readable(Protocol):
    def read(self) -> str: ...


@runtime_checkable
class Writable(Protocol):
    def write(self, content: str) -> None: ...


class File(Readable, Writable, Protocol): ...
