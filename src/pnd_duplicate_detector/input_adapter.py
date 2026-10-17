"""Adapters for the PND cut template and its normalized query output."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .service import REQUIRED_COLUMNS


@dataclass(frozen=True)
class AdaptedInput:
    """Canonical proposals plus a label that identifies the source structure."""

    proposals: pd.DataFrame
    source_format: str


def adapt_input(frame: pd.DataFrame) -> AdaptedInput:
    """Return canonical proposals from direct, Consulta or corte input layouts."""
    data = frame.copy()
    data.columns = [str(name).strip().lower() for name in data.columns]
    if set(REQUIRED_COLUMNS).issubset(data.columns):
        return AdaptedInput(_select_canonical(data), "Formato canonico")
    if {"id_propuesta", "p_propuesta"}.issubset(data.columns):
        return AdaptedInput(_adapt_consulta(data), "Hoja Consulta")
    if {"radicado", "eje1_propuesta"}.issubset(data.columns):
        return AdaptedInput(_adapt_corte(data), "Hoja corte")
    expected = ", ".join(REQUIRED_COLUMNS)
    raise ValueError(
        "No se reconoce el formato. Cargue una hoja Consulta, una hoja corte o columnas: " + expected
    )


def _select_canonical(data: pd.DataFrame) -> pd.DataFrame:
    selected = data.loc[:, [*REQUIRED_COLUMNS]].copy()
    selected["expected_result"] = data.get("expected_result", "")
    return selected


def _adapt_consulta(data: pd.DataFrame) -> pd.DataFrame:
    proposal = data["p_propuesta"]
    municipality = _first_available(data, "p_mcpio_nombre", "c_mcpio_nombre", "p_mcpio_codigo")
    axis = _first_available(data, "eje_vigente", "eje_original", "bloque_origen", "p_tema")
    adapted = pd.DataFrame(
        {
            "proposal_id": data["id_propuesta"],
            "municipality": municipality,
            "axis": axis,
            "proposal": proposal,
            "expected_result": data.get("p_resultado", ""),
        }
    )
    return adapted.loc[_has_content(adapted["proposal"])].reset_index(drop=True)


def _adapt_corte(data: pd.DataFrame) -> pd.DataFrame:
    records: list[pd.DataFrame] = []
    for block in range(1, 9):
        proposal_column = f"eje{block}_propuesta"
        if proposal_column not in data:
            continue
        proposal = data[proposal_column]
        present = _has_content(proposal)
        if not present.any():
            continue
        municipality_code = _first_available(data, f"eje{block}_mcpio")
        department_code = _first_available(data, f"eje{block}_dpto")
        municipality = _join_location(department_code, municipality_code)
        axis = pd.Series(f"bloque_{block}", index=data.index, dtype="object")
        identifier = data["radicado"].map(_clean_identifier) + f"::bloque_{block}"
        records.append(
            pd.DataFrame(
                {
                    "proposal_id": identifier[present],
                    "municipality": municipality[present],
                    "axis": axis[present],
                    "proposal": proposal[present],
                    "expected_result": _first_available(data, f"eje{block}_resultado")[present],
                }
            )
        )
    if not records:
        return pd.DataFrame(columns=[*REQUIRED_COLUMNS, "expected_result"])
    adapted = pd.concat(records, ignore_index=True)
    if adapted["proposal_id"].duplicated().any():
        adapted["proposal_id"] = adapted["proposal_id"] + "::" + adapted.groupby("proposal_id").cumcount().astype(str)
    return adapted


def _first_available(data: pd.DataFrame, *columns: str) -> pd.Series:
    result = pd.Series("", index=data.index, dtype="object")
    for column in columns:
        if column in data:
            candidate = data[column].fillna("").astype(str).str.strip()
            result = result.where(_has_content(result), candidate)
    return result


def _has_content(values: pd.Series) -> pd.Series:
    return values.fillna("").astype(str).str.strip().ne("")


def _clean_identifier(value: object) -> str:
    text = str(value).strip()
    if text.endswith(".0") and text[:-2].isdigit():
        return text[:-2]
    return text


def _join_location(department: pd.Series, municipality: pd.Series) -> pd.Series:
    department_text = department.map(_clean_identifier)
    municipality_text = municipality.map(_clean_identifier)
    return department_text + "-" + municipality_text
