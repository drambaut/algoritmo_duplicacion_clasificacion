"""Threshold tuning from human-reviewed pairs."""

from __future__ import annotations

import pandas as pd


def recommend_threshold(reviewed_pairs: pd.DataFrame) -> tuple[float, float]:
    """Return the score threshold with highest F1 and its corresponding F1."""
    required = {"puntaje_final", "es_duplicado"}
    missing = required.difference(reviewed_pairs.columns)
    if missing:
        raise ValueError(f"Faltan columnas: {', '.join(sorted(missing))}.")
    labels = reviewed_pairs["es_duplicado"].astype(bool)
    if labels.nunique() < 2:
        raise ValueError("La muestra necesita al menos un duplicado y un no duplicado.")
    best_threshold, best_f1 = 0.0, -1.0
    for threshold in sorted(reviewed_pairs["puntaje_final"].unique()):
        predicted = reviewed_pairs["puntaje_final"] >= threshold
        true_positive = int((predicted & labels).sum())
        false_positive = int((predicted & ~labels).sum())
        false_negative = int((~predicted & labels).sum())
        denominator = 2 * true_positive + false_positive + false_negative
        f1 = 2 * true_positive / denominator if denominator else 0.0
        if f1 > best_f1:
            best_threshold, best_f1 = float(threshold), f1
    return best_threshold, best_f1
