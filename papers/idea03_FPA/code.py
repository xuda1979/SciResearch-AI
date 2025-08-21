"""
Example code for Field-Programmable Attention (FPA) demonstration.

This script uses the sciresearch_ai module to compute a simple
field-programmable attention mask for a given sequence length.
"""

from sciresearch_ai import __version__


def generate_attention_mask(length: int, block_size: int = 64):
    """
    Generate a simple block-sparse attention mask.
    This function divides the sequence into blocks and returns
    a list of allowed attention indices for each position.
    """
    mask = []
    for i in range(length):
        block_start = (i // block_size) * block_size
        block_end = min(block_start + block_size, length)
        # Each position can attend to tokens within its block.
        mask.append(list(range(block_start, block_end)))
    return mask


def main():
    length = 256  # example sequence length
    block_size = 64
    mask = generate_attention_mask(length, block_size)
    print(f"sciresearch_ai version: {__version__}")
    print(
        f"Generated FPA mask for sequence length {length} with block size {block_size}."
    )
    print("First three mask entries:", mask[:3], "...")


if __name__ == "__main__":
    main()
