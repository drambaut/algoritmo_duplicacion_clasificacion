import pandas as pd
import numpy as np

from pnd_duplicate_detector.models import DetectionConfig
from pnd_duplicate_detector.service import find_duplicate_pairs


def proposals() -> pd.DataFrame:
    rows = [
        ("a", "Almeida", "Infraestructura", "Arreglar las vias veredales", ""),
        ("b", "Almeida", "Infraestructura", "Arreglar vias veredlales", ""),
        ("c", "Sogamoso", "Infraestructura", "Arreglar las vias veredales", ""),
    ]
    return pd.DataFrame(rows, columns=["proposal_id", "municipality", "axis", "proposal", "expected_result"])


def test_only_compares_proposals_in_the_same_block() -> None:
    pairs = find_duplicate_pairs(proposals(), DetectionConfig(semantic_weight=0.0))
    assert len(pairs) == 1
    assert set(pairs.loc[0, ["proposal_id_a", "proposal_id_b"]]) == {"a", "b"}


def test_score_renormalizes_when_semantic_model_is_not_enabled() -> None:
    pairs = find_duplicate_pairs(proposals(), DetectionConfig(lexical_weight=0.4, jaccard_weight=0.3, semantic_weight=0.3))
    row = pairs.iloc[0]
    expected = (0.4 * row.coseno_lexico + 0.3 * row.jaccard_fragmentos) / 0.7
    assert abs(row.puntaje_final - expected) < 1e-9
    assert pd.isna(row.coseno_semantico)


class FixedEncoder:
    def encode(self, texts: list[str]) -> np.ndarray:
        return np.array([[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]])


def test_includes_semantic_cosine_when_an_encoder_is_supplied() -> None:
    data = proposals().assign(municipality="Almeida")
    pairs = find_duplicate_pairs(data, DetectionConfig(), FixedEncoder())
    semantic_pair = pairs[(pairs.proposal_id_a == "a") & (pairs.proposal_id_b == "b")].iloc[0]
    unrelated_pair = pairs[(pairs.proposal_id_a == "a") & (pairs.proposal_id_b == "c")].iloc[0]
    assert semantic_pair.coseno_semantico > unrelated_pair.coseno_semantico
