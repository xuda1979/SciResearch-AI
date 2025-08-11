from __future__ import annotations
import os, shutil
from sciresearch_ai.project import Project
from sciresearch_ai.config import RunConfig
from sciresearch_ai.orchestrator import Orchestrator
from sciresearch_ai.providers.mock_provider import MockProvider


def run_smoke(tmp_root: str) -> str:
    if os.path.exists(tmp_root):
        shutil.rmtree(tmp_root)
    os.makedirs(tmp_root, exist_ok=True)
    prj = Project.create(tmp_root, "unit_demo")
    cfg = RunConfig(max_iterations=2, samples_per_query=3, interactive=False)
    orch = Orchestrator(prj, MockProvider(), cfg)
    orch.run()
    # check files
    assert os.path.exists(os.path.join(prj.root, "paper", "draft.tex"))
    assert os.path.exists(os.path.join(prj.root, "revisions"))
    # return path for inspection
    return prj.root


def test_run_smoke(tmp_path):
    run_smoke(str(tmp_path))


