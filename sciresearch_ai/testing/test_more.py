from __future__ import annotations

import glob
import os

from sciresearch_ai.config import RunConfig
from sciresearch_ai.inference.ttc import budgeted_adaptive_deliberation
from sciresearch_ai.orchestrator import Orchestrator
from sciresearch_ai.project import Project
from sciresearch_ai.providers.mock_provider import MockProvider


def test_autosave_and_checkpoints(tmp_path):
    tmp_dir = tmp_path
    prj = Project.create(str(tmp_dir), "autosave_demo")
    cfg = RunConfig(max_iterations=2, samples_per_query=3, interactive=False)
    orch = Orchestrator(prj, MockProvider(), cfg)
    orch.run()
    revs = glob.glob(os.path.join(prj.root, "revisions", "draft-*.tex"))
    assert len(revs) >= 2, "Expect at least one snapshot per iteration"


def test_bad_early_stop():
    # If scorer strongly prefers longer text, one batch may suffice
    def fake_gen(prompt, n):
        return [("A" * 50) if i == 0 else "b" for i in range(n)]

    def scorer(s):
        return len(s)

    out = budgeted_adaptive_deliberation(
        fake_gen,
        "x",
        total_budget=4,
        batch_size=2,
        scorer=scorer,
        early_stop_margin=1.0,
    )
    assert out["best"], "Should pick a best sample"
