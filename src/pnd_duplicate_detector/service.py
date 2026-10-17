"""Validation, grouping and traceable pair scoring."""

from __future__ import annotations

from itertools import combinations
from typing import Iterable

import numpy as np
import pandas as pd

from .models import DetectionConfig
from .similarity import SemanticEncoder, cosine_similarity_vectors, jaccard_shingles, lexical_cosine
from .text import normalize_text

REQUIRED_COLUMNS = ("proposal_id", "municipality", "axis", "proposal")


def validate_proposals(proposals: pd.DataFrame) -> pd.DataFrame:
    missing = [name for name in REQUIRED_COLUMNS if name not in proposals.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(missing)}.")
    if proposals["proposal_id"].isna().any() or proposals["proposal_id"].duplicated().any():
        raise ValueError("proposal_id debe existir y ser unico.")
    if proposals[list(REQUIRED_COLUMNS[1:])].isna().any().any():
        raise ValueError("municipality, axis y proposal no pueden estar vacios.")
    checked = proposals.copy()
    for name in REQUIRED_COLUMNS:
        if checked[name].astype(str).str.strip().eq("").any():
            raise ValueError(f"{name} no puede contener valores vacios.")
    if "expected_result" not in checked:
        checked["expected_result"] = ""
    return checked


def _comparison_text(row: pd.Series, include_expected_result: bool) -> str:
    proposal = str(row["proposal"])
    if include_expected_result and pd.notna(row.get("expected_result")):
        return f"{proposal} {row['expected_result']}"
    return proposal


def _blocks(proposals: pd.DataFrame, block_by_axis: bool) -> Iterable[pd.DataFrame]:
    keys = ["_municipality_key"] + (["_axis_key"] if block_by_axis else [])
    yield from (group for _, group in proposals.groupby(keys, dropna=False, sort=False))


def _status(score: float, config: DetectionConfig) -> str:
    if score >= config.duplicate_threshold:
        return "posible_duplicado"
    if score >= config.review_threshold:
        return "revisar"
    return "sin_alerta"


def _combined_score(scores: dict[str, float], config: DetectionConfig, semantic_active: bool) -> float:
    weighted = [
        (scores["coseno_lexico"], config.lexical_weight),
        (scores["jaccard_fragmentos"], config.jaccard_weight),
    ]
    if semantic_active:
        weighted.append((scores["coseno_semantico"], config.semantic_weight))
    total_weight = sum(weight for _, weight in weighted)
    return sum(value * weight for value, weight in weighted) / total_weight if total_weight else 0.0


def find_duplicate_pairs(
    proposals: pd.DataFrame,
    config: DetectionConfig | None = None,
    semantic_encoder: SemanticEncoder | None = None,
) -> pd.DataFrame:
    """Return within-group pairs with component scores and a review status."""
    config = config or DetectionConfig()
    data = validate_proposals(proposals)
    data["_municipality_key"] = data["municipality"].map(normalize_text)
    data["_axis_key"] = data["axis"].map(normalize_text)
    data["_text"] = data.apply(
        _comparison_text, axis=1, include_expected_result=config.include_expected_result
    )

    vectors_by_id: dict[object, np.ndarray] = {}
    if semantic_encoder is not None:
        vectors = semantic_encoder.encode(data["_text"].tolist())
        if len(vectors) != len(data):
            raise ValueError("El codificador semantico devolvio una cantidad incorrecta de vectores.")
        vectors_by_id = dict(zip(data["proposal_id"], vectors, strict=True))

    rows: list[dict[str, object]] = []
    for block in _blocks(data, config.block_by_axis):
        for (_, left), (_, right) in combinations(block.iterrows(), 2):
            scores: dict[str, float] = {
                "coseno_lexico": lexical_cosine(left["_text"], right["_text"]),
                "jaccard_fragmentos": jaccard_shingles(left["_text"], right["_text"], config.shingle_size),
                "coseno_semantico": np.nan,
            }
            if semantic_encoder is not None:
                scores["coseno_semantico"] = cosine_similarity_vectors(
                    vectors_by_id[left["proposal_id"]], vectors_by_id[right["proposal_id"]]
                )
            final_score = _combined_score(scores, config, semantic_encoder is not None)
            rows.append(
                {
                    "proposal_id_a": left["proposal_id"],
                    "proposal_id_b": right["proposal_id"],
                    "municipality": left["municipality"],
                    "axis": left["axis"],
                    "proposal_a": left["proposal"],
                    "proposal_b": right["proposal"],
                    **scores,
                    "puntaje_final": final_score,
                    "estado": _status(final_score, config),
                }
            )

    columns = [
        "proposal_id_a", "proposal_id_b", "municipality", "axis", "proposal_a", "proposal_b",
        "coseno_lexico", "jaccard_fragmentos", "coseno_semantico", "puntaje_final", "estado",
    ]
    result = pd.DataFrame(rows, columns=columns)
    if result.empty:
        return result
    result = _keep_top_neighbors(result, config.top_k_neighbors)
    return result.sort_values("puntaje_final", ascending=False, ignore_index=True)


def _keep_top_neighbors(pairs: pd.DataFrame, top_k: int | None) -> pd.DataFrame:
    if top_k is None:
        return pairs
    retained: set[int] = set()
    for key in ("proposal_id_a", "proposal_id_b"):
        for _, group in pairs.groupby(key, sort=False):
            retained.update(group.nlargest(top_k, "puntaje_final").index)
    return pairs.loc[sorted(retained)].copy()


def detection_summary(pairs: pd.DataFrame) -> dict[str, int]:
    if pairs.empty:
        return {"parejas_evaluadas": 0, "posibles_duplicados": 0, "para_revision": 0}
    return {
        "parejas_evaluadas": len(pairs),
        "posibles_duplicados": int((pairs["estado"] == "posible_duplicado").sum()),
        "para_revision": int((pairs["estado"] == "revisar").sum()),
    }
