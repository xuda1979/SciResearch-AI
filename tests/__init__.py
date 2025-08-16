import os
import sys

# Ensure the standalone CLI package is importable during tests
pkg_root = os.path.join(os.path.dirname(__file__), "..", "packages", "sciresearch-cli")
sys.path.insert(0, os.path.abspath(pkg_root))
