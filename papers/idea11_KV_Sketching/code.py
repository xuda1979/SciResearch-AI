"""
Key‑Value Sketching example.

This script demonstrates low‑rank compression of a K/V matrix using truncated
SVD, then reconstructs an approximate matrix.
"""

import numpy as np

# Import sciresearch_ai to demonstrate usage of the repository as a package.
try:
    import sciresearch_ai  # type: ignore
    version = getattr(sciresearch_ai, "__version__", "unknown")
except Exception:
    sciresearch_ai = None  # type: ignore
    version = "unknown"

from typing import Tuple


def svd_sketch(matrix: np.ndarray, rank: int = 2) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Return a low‑rank sketch of the input matrix using truncated SVD.

    Args:
        matrix (np.ndarray): The original matrix to compress.
        rank (int): Number of singular values/vectors to keep.

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]: The truncated (U, S, Vh).
    """
    u, s, vh = np.linalg.svd(matrix, full_matrices=False)
    u_r = u[:, :rank]
    s_r = s[:rank]
    vh_r = vh[:rank, :]
    return u_r, s_r, vh_r


def reconstruct(u_r: np.ndarray, s_r: np.ndarray, vh_r: np.ndarray) -> np.ndarray:
    """
    Rehydrate an approximate matrix from its low‑rank sketch.

    Args:
        u_r (np.ndarray): Truncated left singular vectors.
        s_r (np.ndarray): Truncated singular values.
        vh_r (np.ndarray): Truncated right singular vectors.

    Returns:
        np.ndarray: The reconstructed approximate matrix.
    """
    return (u_r @ np.diag(s_r)) @ vh_r


def main() -> None:
    """Demonstrate key‑value sketching via truncated SVD."""
    state = np.random.rand(10, 5)  # Example K/V state matrix (10 tokens × 5 dims)
    u_r, s_r, vh_r = svd_sketch(state, rank=2)
    approx = reconstruct(u_r, s_r, vh_r)
    error = np.linalg.norm(state - approx)
    print("Demo of KV sketching via truncated SVD")
    print("Original matrix:\n", state)
    print("Approximation:\n", approx)
    print(f"Approximation error: {error:.4f}")
    print("sciresearch_ai module loaded, version:", version)


if __name__ == "__main__":
    main()