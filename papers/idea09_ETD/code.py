"""
Example of entropy-thermostat decoding for idea09 (Entropy-Thermostat Decoding).
This script generates random probability distributions for token probabilities, computes
entropy at each step, and adjusts a temperature parameter based on the entropy target.
It also prints the version of the sciresearch_ai module being used.
"""

from sciresearch_ai import __version__
import random
import math

print(f"Using sciresearch_ai version {__version__}")

# Function to compute entropy of a probability distribution.
def entropy(probs):
    return -sum(p * math.log(p + 1e-12) for p in probs)

# Generate a sequence of random probability distributions
def generate_prob_sequences(num_steps=5, vocab_size=5):
    sequences = []
    for _ in range(num_steps):
        # Random probabilities
        values = [random.random() for _ in range(vocab_size)]
        total = sum(values)
        probs = [v / total for v in values]
        sequences.append(probs)
    return sequences

# Simple thermostat that adjusts temperature based on entropy
# If entropy is above the target, decrease temperature (makes distribution sharper)
# If entropy is below the target, increase temperature (makes distribution smoother)
def thermostat_decode(prob_sequences, target_entropy=1.0):
    temperature = 1.0
    for step, probs in enumerate(prob_sequences, 1):
        ent = entropy(probs)
        if ent > target_entropy:
            temperature *= 0.9
        else:
            temperature *= 1.1
        print(f"Step {step}: entropy={ent:.3f}, temperature={temperature:.3f}")
    return temperature

if __name__ == "__main__":
    # Generate example probabilities and run the thermostat
    prob_sequences = generate_prob_sequences(num_steps=8, vocab_size=6)
    final_temp = thermostat_decode(prob_sequences, target_entropy=1.5)
    print(f"Final temperature: {final_temp:.3f}")
