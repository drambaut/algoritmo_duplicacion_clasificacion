"""The three similarity measures described in the supplied slides."""

from __future__ import annotations

from collections import Counter
from math import sqrt
from typing import Protocol, Sequence

import numpy as np

from .text import character_shingles, token_counts


def cosine_similarity_counts(left: Counter[str], right: Counter[str]) -> float:
    """Cosine over word-count vectors."""
    if not left or not right:
        return 0.0
    dot_product = sum(left[term] * right.get(term, 0) for term in left)
    left_norm = sqrt(sum(count * count for count in left.values()))
    right_norm = sqrt(sum(count * count for count in right.values()))
    return dot_product / (left_norm * right_norm) if left_norm and right_norm else 0.0


def lexical_cosine(left: object, right: object) -> float:
    return cosine_similarity_counts(token_counts(left), token_counts(right))


def jaccard_shingles(left: object, right: object, size: int = 5) -> float:
    """Jaccard over sets of character shingles."""
    left_parts = character_shingles(left, size)
    right_parts = character_shingles(right, size)
    union = left_parts | right_parts
    return len(left_parts & right_parts) / len(union) if union else 0.0


class SemanticEncoder(Protocol):
    """Contract for a local embedding provider."""

    def encode(self, texts: Sequence[str]) -> np.ndarray: ...


class SentenceTransformerEncoder:
    """Optional adapter for an on-premise Sentence-Transformers model."""

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as error:  # pragma: no cover
            raise RuntimeError("Instale el extra semantic: pip install -e .[semantic]") from error
        self._model = SentenceTransformer(model_name)

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        return np.asarray(self._model.encode(list(texts), normalize_embeddings=True))


def cosine_similarity_vectors(left: np.ndarray, right: np.ndarray) -> float:
    """Vector cosine clamped to the [0, 1] scale used by the other metrics."""
    norm = float(np.linalg.norm(left) * np.linalg.norm(right))
    if norm == 0:
        return 0.0
    return max(0.0, float(np.dot(left, right) / norm))
