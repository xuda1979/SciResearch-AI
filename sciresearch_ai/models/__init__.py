"""Model wrappers for SciResearch-AI."""
from .oss_120b import load_model as load_oss_120b, load_local_generator

__all__ = ["load_oss_120b", "load_local_generator"]
