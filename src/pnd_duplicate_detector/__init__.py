"""Explainable tools to find likely duplicate PND proposals."""

from .models import DetectionConfig
from .service import find_duplicate_pairs

__all__ = ["DetectionConfig", "find_duplicate_pairs"]
