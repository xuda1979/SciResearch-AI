#!/usr/bin/env bash

# Script to automate training of the Texas Hold'em AI on GPU or TPU.
# It clones the repository, installs dependencies, and starts a small
# training run.  Adjust NUM_HANDS and other flags to meet your needs.

set -euo pipefail

# URL of the open source project implementing Texas Hold'em AI.
REPO_URL="https://github.com/xuda1979/texas_holdem_ai_gatc.git"

# Training parameters.  Use a very small number of hands for a quick
# demonstration.  Increase these values for real training runs.
NUM_HANDS=${NUM_HANDS:-1}
ALGO="ai_cfr"
MIN_BUFFER=16

# Clone the repository if it hasn't been cloned already.
if [ ! -d "texas_holdem_ai_gatc" ]; then
  echo "Cloning repository ${REPO_URL}..."
  git clone "${REPO_URL}"
fi

cd texas_holdem_ai_gatc || {
  echo "Failed to enter repository directory" >&2
  exit 1
}

# Install the Python dependencies.  Use --quiet to reduce output noise.
echo "Installing Python dependencies..."
pip install -r requirements.txt --quiet

# Compose the base training command.  These flags come from the
# repository's training CLI which supports specifying the number
# of hands, algorithm, and the minimum buffer before training.
TRAIN_CMD="python -m poker_ai.cli.train --num-hands ${NUM_HANDS} \
  --algorithm ${ALGO} --min-buffer-before-train ${MIN_BUFFER}"

# Detect TPU availability by looking for the COLAB_TPU_ADDR environment
# variable.  This variable is set by Google Colab when a TPU is
# provisioned.  If it's present, install torch_xla and run on the TPU.
if [ -n "${COLAB_TPU_ADDR:-}" ]; then
  echo "TPU detected at ${COLAB_TPU_ADDR}. Installing torch_xla..."
  # Ensure that PyTorch and torch_xla versions match.  Adjust the
  # version numbers if necessary.  Use quiet mode to minimize output.
  pip install "torch==2.2.0" --quiet
  pip install "torch_xla[tpu]==2.2.0" \
    -f https://storage.googleapis.com/libtpu-releases/index.html --quiet
  echo "Starting training on TPU..."
  eval "${TRAIN_CMD} --tpu"
else
  echo "No TPU detected.  Attempting to use GPU if available."
  # GPU training is enabled via the --gpus flag.  If no GPU is
  # available, the script will fall back to CPU execution.
  echo "Starting training on GPU/CPU..."
  eval "${TRAIN_CMD} --gpus"
fi
