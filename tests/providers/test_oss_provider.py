import sys

import sciresearch_ai.providers.oss_provider as mod


def test_stub_backend_selected(monkeypatch):
    called = {}

    def fake_setup_transformers(checkpoint, device=None):
        called["transformers"] = True
        return lambda tokens, temperature=0.0, new_request=False: 0

    monkeypatch.setenv("OSS_PROVIDER_BACKEND", "stub")
    monkeypatch.setattr(mod, "_setup_transformers", fake_setup_transformers)

    sys.modules.pop("openai_harmony", None)
    prov = mod.OssProvider()

    assert "transformers" not in called
    assert "openai_harmony" not in sys.modules
    assert prov.generate("hi") == [
        "This is a demo response from the OSS provider stub."
    ]
