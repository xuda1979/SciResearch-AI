"""
Field‑Programmable Attention (FPA) example.

This script generates a block‑sparse attention mask that restricts each token to
attend within its block.
"""

try:
    from sciresearch_ai import __version__ as _version  # type: ignore
except Exception:
    _version = "unknown"


def generate_attention_mask(length: int, block_size: int = 64) -> list[list[int]]:
    """
    Generate a block‑sparse attention mask.

    Args:
        length (int): Length of the sequence.
        block_size (int): Size of each block.

    Returns:
        List[List[int]]: A list of allowed attention indices for each position.
    """
    mask: list[list[int]] = []
    for i in range(length):
        block_start = (i // block_size) * block_size
        block_end = min(block_start + block_size, length)
        mask.append(list(range(block_start, block_end)))
    return mask


def main() -> None:
    """Demonstrate FPA mask generation."""
    length = 256
    block_size = 64
    mask = generate_attention_mask(length, block_size)
    print(f"sciresearch_ai version: {_version}")
    print(
        f"Generated FPA mask for sequence length {length} with block size {block_size}."
    )
    print("First three mask entries:", mask[:3], "...")


if __name__ == "__main__":
    main()
