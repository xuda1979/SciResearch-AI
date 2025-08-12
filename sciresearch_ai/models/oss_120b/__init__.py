from __future__ import annotations
from typing import Optional, Tuple

try:  # pragma: no cover - optional dependency
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception:  # transformers may be missing during tests
    AutoModelForCausalLM = AutoTokenizer = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from gpt_oss.tokenizer import get_tokenizer as _gpt_tokenizer
    from gpt_oss.torch.model import TokenGenerator as _TorchGenerator
except Exception:  # gpt_oss or torch may be missing
    _gpt_tokenizer = None
    _TorchGenerator = None

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
        raise RuntimeError(
            "transformers is required to load the OSS 120B model"
        )
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
                raise RuntimeError(
                    "torch-npu is required for NPU execution"
                ) from exc
        else:
            try:
                import torch
                model.to(device)
            except Exception as exc:  # pragma: no cover - optional dep
                raise RuntimeError(
                    f"Unable to move model to device {device!r}"
                ) from exc
    return model, tokenizer


def load_local_generator(checkpoint: str) -> Tuple[object, object]:
    """Load the tokenizer and token generator from the vendored ``gpt_oss``.

    Parameters
    ----------
    checkpoint:
        Path to a local SafeTensors checkpoint for the OSS 120B model.

    Returns
    -------
    (generator, tokenizer):
        Instances suitable for token-by-token generation using the
        official ``gpt_oss`` implementation.
    """
    if _gpt_tokenizer is None or _TorchGenerator is None:
        raise RuntimeError(
            "gpt_oss with torch backend is required to load the local generator"
        )
    tokenizer = _gpt_tokenizer()
    generator = _TorchGenerator(checkpoint)
    return generator, tokenizer
