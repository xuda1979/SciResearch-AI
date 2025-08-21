"""
Demo for Semantic-Hash Lattice Memory (SHL-Mem).

This script simulates a simple semantic-hash lattice memory by hashing
random token spans into buckets and performing intersection to retrieve
related tokens.
"""

from sciresearch_ai import __version__
import random


def generate_hashes(num_spans: int, num_functions: int = 3, hash_space: int = 10):
    """
    Generate random hash codes for each span under multiple hash functions.
    Returns a list of lists where each inner list contains hash codes for a span.
    """
    return [
        [random.randint(0, hash_space - 1) for _ in range(num_functions)]
        for _ in range(num_spans)
    ]


def retrieve_by_intersection(hashes, query_code):
    """
    Retrieve indices of spans whose hash codes match the query on all functions.
    """
    matches = []
    for idx, codes in enumerate(hashes):
        if all(c == qc for c, qc in zip(codes, query_code)):
            matches.append(idx)
    return matches


def main():
    num_spans = 20
    hashes = generate_hashes(num_spans)
    # choose a random span as query
    query_index = random.randint(0, num_spans - 1)
    query_code = hashes[query_index]
    matches = retrieve_by_intersection(hashes, query_code)
    print(f"sciresearch_ai version: {__version__}")
    print(f"Generated {num_spans} spans with 3 hash functions.")
    print(f"Query span index: {query_index}, query code: {query_code}")
    print(f"Retrieved matches: {matches}")


if __name__ == "__main__":
    main()
