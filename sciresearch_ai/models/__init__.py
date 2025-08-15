"""Model wrappers for SciResearch-AI."""

from .oss_120b import load_local_generator
from .oss_120b import load_model as load_oss_120b

__all__ = ["load_oss_120b", "load_local_generator"]
