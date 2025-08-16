def test_auto_provider_oss():
    from sciresearch_ai.main import _auto_provider

    assert _auto_provider("oss-120b") == "oss"


def test_auto_provider_openai():
    from sciresearch_ai.main import _auto_provider

    assert _auto_provider("o3-mini") == "openai"


def test_auto_provider_mock():
    from sciresearch_ai.main import _auto_provider

    assert _auto_provider(None) == "mock"
