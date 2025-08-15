import os
import sys
import zipfile

sys.path.insert(0, r"/mnt/data/SciResearch-AI")
import tempfile

from sciresearch_ai.testing.test_mock_flow import run_smoke

if __name__ == "__main__":
    tmp_root = tempfile.mkdtemp(prefix="sci_demo_")
    path = run_smoke(tmp_root)
    zpath = os.path.join(os.path.dirname(path), "unit_demo.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(path):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, os.path.dirname(path))
                zf.write(full, rel)
    print("Demo project created at:", path)
    print("Zip at:", zpath)
