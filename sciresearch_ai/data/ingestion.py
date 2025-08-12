from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, Optional


@dataclass
class DatasetRecord:
    """Normalized record for RL fine-tuning data."""

    provider: str
    prompt: str
    response: str
    metadata: Dict[str, Any]


def normalize_record(
    provider: str,
    prompt: str,
    response: Any,
    metadata: Optional[Dict[str, Any]] = None,
) -> DatasetRecord:
    """Create a :class:`DatasetRecord` from raw provider output.

    Parameters
    ----------
    provider:
        Name of the provider, e.g., ``"gpt-5"``, ``"gemini-2.5"`` or
        ``"oss-120b"``.
    prompt:
        The prompt text submitted to the provider.
    response:
        Raw response object. Non-string responses are serialized to JSON.
    metadata:
        Optional free-form metadata (e.g., timestamps, temperatures).
    """
    if not isinstance(response, str):
        try:
            response = json.dumps(response)
        except Exception:
            response = str(response)
    return DatasetRecord(
        provider=provider,
        prompt=prompt,
        response=response,
        metadata=metadata or {},
    )


def ingest_records(records: Iterable[DatasetRecord], path: str) -> None:
    """Append records to a JSONL file."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(asdict(rec)) + "\n")
