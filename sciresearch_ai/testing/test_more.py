from __future__ import annotations
import os, shutil, time, glob
from sciresearch_ai.project import Project
from sciresearch_ai.config import RunConfig
from sciresearch_ai.orchestrator import Orchestrator
from sciresearch_ai.providers.mock_provider import MockProvider
from sciresearch_ai.inference.ttc import budgeted_adaptive_deliberation

def test_autosave_and_checkpoints(tmp_dir: str):
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)
    prj = Project.create(tmp_dir, "autosave_demo")
    cfg = RunConfig(max_iterations=2, samples_per_query=3, interactive=False)
    orch = Orchestrator(prj, MockProvider(), cfg)
    orch.run()
    revs = glob.glob(os.path.join(prj.root, "revisions", "draft-*.tex"))
    assert len(revs) >= 2, "Expect at least one snapshot per iteration"

def test_bad_early_stop():
    # If scorer strongly prefers longer text, one batch may suffice
    def fake_gen(prompt, n):
        return [("A"*50) if i==0 else "b" for i in range(n)]
    def scorer(s): return len(s)
    out = budgeted_adaptive_deliberation(fake_gen, "x", total_budget=4, batch_size=2, scorer=scorer, early_stop_margin=1.0)
    assert out["best"], "Should pick a best sample"

if __name__ == "__main__":
    d = os.path.join(os.getcwd(), "tmp_tests")
    test_autosave_and_checkpoints(d)
    test_bad_early_stop()
    print("Additional tests passed.")
