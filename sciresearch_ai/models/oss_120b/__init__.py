from __future__ import annotations

from typing import Optional, Tuple

try:  # pragma: no cover - optional dependency
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception:  # transformers may be missing during tests
    AutoModelForCausalLM = AutoTokenizer = None  # type: ignore

DEFAULT_MODEL_NAME = "openai/oss-120b"


def load_model(
    model_name_or_path: Optional[str] = None,
    device: Optional[str] = None,
) -> Tuple[object, object]:
    """Load the OSS 120B model and tokenizer via ``transformers``.

    Parameters
    ----------
    model_name_or_path:
        Local path or Hugging Face model identifier. Defaults to
        ``openai/oss-120b``.
    device:
        Optional device specifier (e.g. ``"cuda"``, ``"cpu"``, ``"npu"``).

    Returns
    -------
    (model, tokenizer):
        The causal language model and corresponding tokenizer. If the
        transformers dependency is missing, a ``RuntimeError`` is raised.
    """
    if AutoModelForCausalLM is None or AutoTokenizer is None:
        raise RuntimeError("transformers is required to load the OSS 120B model")
    name = model_name_or_path or DEFAULT_MODEL_NAME
    tokenizer = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(name)
    if device:
        if device.lower() == "npu":
            try:
                import torch
                import torch_npu  # noqa: F401  register NPU backend

                model.to("npu")
            except Exception as exc:  # pragma: no cover - optional dep
                raise RuntimeError("torch-npu is required for NPU execution") from exc
        else:
            try:
                import torch

                model.to(device)
            except Exception as exc:  # pragma: no cover - optional dep
                raise RuntimeError(
                    f"Unable to move model to device {device!r}"
                ) from exc
    return model, tokenizer


def load_local_generator() -> callable:  # pragma: no cover - simple stub
    """Return a lightweight text generator for tests.

    The real OSS 120B model is far too heavy for unit tests.  This
    helper provides a minimal callable with a compatible interface so
    that modules depending on ``load_local_generator`` can run in
    environments without the large model or the ``transformers``
    library."""

    def _generator(prompt: str, **_: object) -> str:
        return "stub"

    return _generator
