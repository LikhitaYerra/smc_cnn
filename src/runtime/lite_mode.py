"""Runtime flags for cloud deployment."""

from __future__ import annotations

import os


def is_lite_mode() -> bool:
    """True when running without PyTorch (Render free tier, etc.)."""
    return os.getenv("LITE_MODE", "").lower() in {"1", "true", "yes"}
