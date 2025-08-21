import numpy as np

# Import the sciresearch_ai module to demonstrate usage of the repository as a package
import sciresearch_ai


def svd_sketch(matrix: np.ndarray, rank: int = 2):
    """Return a low‑rank sketch of the input matrix using truncated SVD.

    Args:
        matrix (np.ndarray): The original matrix to compress.
        rank (int): Number of singular values/vectors to keep.

    Returns:
        Tuple of (u_r, s_r, vh_r) representing the sketch.
    """
    u, s, vh = np.linalg.svd(matrix, full_matrices=False)
    u_r = u[:, :rank]
    s_r = s[:rank]
    vh_r = vh[:rank, :]
    return u_r, s_r, vh_r


def reconstruct(u_r: np.ndarray, s_r: np.ndarray, vh_r: np.ndarray) -> np.ndarray:
    """Rehydrate an approximate matrix from its low‑rank sketch."""
    return (u_r @ np.diag(s_r)) @ vh_r


if __name__ == "__main__":
    # Create a random matrix representing K/V state (10 tokens x 5 dimensions)
    state = np.random.rand(10, 5)
    u_r, s_r, vh_r = svd_sketch(state, rank=2)
    approx = reconstruct(u_r, s_r, vh_r)
    error = np.linalg.norm(state - approx)
    print("Demo of KV sketching via truncated SVD")
    print("Original matrix:\n", state)
    print("Approximation:\n", approx)
    print(f"Approximation error: {error:.4f}")

    # Demonstrate that sciresearch_ai is importable
    print("sciresearch_ai module loaded from version:", getattr(sciresearch_ai, "__version__", "unknown"))
