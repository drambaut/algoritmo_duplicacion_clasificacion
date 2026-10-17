"""Domain models and audit-friendly settings."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DetectionConfig:
    """Parameters for grouping, scoring and alert classification."""

    lexical_weight: float = 0.40
    jaccard_weight: float = 0.30
    semantic_weight: float = 0.30
    duplicate_threshold: float = 0.72
    review_threshold: float = 0.55
    shingle_size: int = 5
    block_by_axis: bool = True
    include_expected_result: bool = True
    top_k_neighbors: int | None = 10

    def __post_init__(self) -> None:
        weights = (self.lexical_weight, self.jaccard_weight, self.semantic_weight)
        if any(weight < 0 for weight in weights) or sum(weights) <= 0:
            raise ValueError("Los pesos deben ser no negativos y alguno debe ser mayor que cero.")
        if not 0 <= self.review_threshold <= self.duplicate_threshold <= 1:
            raise ValueError("Los umbrales deben cumplir 0 <= revision <= duplicado <= 1.")
        if self.shingle_size < 2:
            raise ValueError("El tamano de fragmento debe ser al menos 2.")
        if self.top_k_neighbors is not None and self.top_k_neighbors < 1:
            raise ValueError("top_k_neighbors debe ser positivo o None.")
