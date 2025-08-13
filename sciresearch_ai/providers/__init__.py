try:
    from .oss_provider import OssProvider
except Exception:  # pragma: no cover - optional dependency
    OssProvider = None  # type: ignore

__all__ = ["OssProvider"]
