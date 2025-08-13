from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import sys, types

sys.modules.setdefault("datasets", types.SimpleNamespace(load_dataset=lambda *a, **k: None))

class DummyConfig:
    def __init__(self, *a, **k):
        pass

sys.modules.setdefault(
    "trl", types.SimpleNamespace(PPOConfig=DummyConfig, PPOTrainer=object)
)

import scripts.train_rl as trl


class DummyModel:
    def __init__(self):
        self.device = "cpu"

    def save_pretrained(self, path: str):
        Path(path).mkdir(parents=True, exist_ok=True)
        (Path(path) / "model.bin").write_text("ok")


class DummyTokenizer:
    def save_pretrained(self, path: str):
        Path(path).mkdir(parents=True, exist_ok=True)
        (Path(path) / "tokenizer.json").write_text("{}")


class DummyTrainer:
    def __init__(self, *args, **kwargs):
        pass

    def train(self):
        return None


def test_train_rl_writes_artifacts(tmp_path, monkeypatch):
    data = tmp_path / "data.jsonl"
    data.write_text(json.dumps({"prompt": "hi", "response": "there"}) + "\n")

    monkeypatch.setattr(trl, "load_model", lambda model, device=None: (DummyModel(), DummyTokenizer()))
    monkeypatch.setattr(trl, "load_dataset", lambda format, data_files: {"train": ["dummy"]})
    monkeypatch.setattr(trl, "PPOTrainer", lambda *a, **k: DummyTrainer())

    out = tmp_path / "out"
    args = SimpleNamespace(data=str(data), output=str(out), model=None, device=None)
    monkeypatch.setattr(trl, "parse_args", lambda: args)

    trl.main()

    assert (out / "model.bin").exists()
    assert (out / "tokenizer.json").exists()
