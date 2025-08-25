"""
Semantic‑Hash Lattice Memory (SHL‑Mem) example.

This script simulates hashing random token spans into multiple buckets and
retrieving related spans via intersection.
"""

try:
    from sciresearch_ai import __version__ as _version  # type: ignore
except Exception:
    _version = "unknown"

import random
from typing import List


def generate_hashes(num_spans: int, num_functions: int = 3, hash_space: int = 10) -> List[List[int]]:
    """
    Generate random hash codes for each span under multiple hash functions.

    Args:
        num_spans (int): Number of spans to generate.
        num_functions (int): Number of hash functions.
        hash_space (int): Range of hash values.

    Returns:
        List[List[int]]: A list containing hash codes for each span.
    """
    return [
        [random.randint(0, hash_space - 1) for _ in range(num_functions)]
        for _ in range(num_spans)
    ]


def retrieve_by_intersection(hashes: List[List[int]], query_code: List[int]) -> List[int]:
    """
    Retrieve indices of spans whose hash codes match the query on all functions.

    Args:
        hashes (List[List[int]]): The hash codes of spans.
        query_code (List[int]): The query hash codes to match.

    Returns:
        List[int]: List of indices matching the query.
    """
    matches: List[int] = []
    for idx, codes in enumerate(hashes):
        if all(c == qc for c, qc in zip(codes, query_code)):
            matches.append(idx)
    return matches


def main() -> None:
    """Demonstrate semantic‑hash lattice memory retrieval."""
    num_spans = 20
    hashes = generate_hashes(num_spans)
    query_index = random.randint(0, num_spans - 1)
    query_code = hashes[query_index]
    matches = retrieve_by_intersection(hashes, query_code)
    print(f"sciresearch_ai version: {_version}")
    print(f"Generated {num_spans} spans with 3 hash functions.")
    print(f"Query span index: {query_index}, query code: {query_code}")
    print(f"Retrieved matches: {matches}")


if __name__ == "__main__":
    main()