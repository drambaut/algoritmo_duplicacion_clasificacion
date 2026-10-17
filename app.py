"""Streamlit user interface."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from pnd_duplicate_detector.models import DetectionConfig
from pnd_duplicate_detector.input_adapter import adapt_input
from pnd_duplicate_detector.sample_data import sample_proposals
from pnd_duplicate_detector.service import detection_summary, find_duplicate_pairs
from pnd_duplicate_detector.similarity import SentenceTransformerEncoder

st.set_page_config(page_title="Duplicidad PND", page_icon="🔎", layout="wide")


@st.cache_resource(show_spinner=False)
def load_semantic_encoder() -> SentenceTransformerEncoder:
    return SentenceTransformerEncoder()


def read_upload(uploaded_file: object) -> tuple[pd.DataFrame, str]:
    name = getattr(uploaded_file, "name", "").lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file), "CSV"
    if name.endswith((".xlsx", ".xls")):
        with pd.ExcelFile(uploaded_file) as workbook:
            candidates = [sheet for sheet in workbook.sheet_names if sheet.lower() in {"consulta", "corte"}]
            for sheet in candidates:
                data = pd.read_excel(workbook, sheet_name=sheet)
                if not data.empty:
                    return data, f"Hoja {sheet}"
            sheet = candidates[0] if candidates else workbook.sheet_names[0]
            return pd.read_excel(workbook, sheet_name=sheet), f"Hoja {sheet}"
    raise ValueError("El archivo debe ser CSV, XLSX o XLS.")


def csv_bytes(data: pd.DataFrame) -> bytes:
    return data.to_csv(index=False).encode("utf-8-sig")


st.title("Deteccion de propuestas PND potencialmente duplicadas")
st.caption("Prioriza parejas para revision humana. La aplicacion no elimina ni fusiona propuestas.")

with st.sidebar:
    st.header("Configuracion")
    lexical_weight = st.slider("Peso coseno lexico", 0.0, 1.0, 0.40, 0.05)
    jaccard_weight = st.slider("Peso Jaccard de fragmentos", 0.0, 1.0, 0.30, 0.05)
    semantic_weight = st.slider("Peso coseno semantico", 0.0, 1.0, 0.30, 0.05)
    duplicate_threshold = st.slider("Umbral posible duplicado", 0.0, 1.0, 0.72, 0.01)
    review_threshold = st.slider("Umbral revision", 0.0, duplicate_threshold, min(0.55, duplicate_threshold), 0.01)
    block_by_axis = st.checkbox("Comparar solo en el mismo eje", value=True)
    use_semantic_model = st.checkbox("Usar modelo semantico local", value=False)

if not use_semantic_model:
    st.caption("Sin modelo semantico, el puntaje reescala los pesos lexico y Jaccard.")

uploaded = st.file_uploader("Cargue propuestas en CSV o Excel", type=["csv", "xlsx", "xls"])
if uploaded is None:
    adapted = adapt_input(sample_proposals())
    proposals = adapted.proposals
    source_label = "Datos sinteticos"
    st.info("Mostrando datos sinteticos. Cargue un archivo para analizar sus propuestas.")
else:
    try:
        raw_input, sheet_label = read_upload(uploaded)
        adapted = adapt_input(raw_input)
        proposals = adapted.proposals
        source_label = f"{sheet_label}. {adapted.source_format}"
    except Exception as error:
        st.error(f"No se pudo leer el archivo: {error}")
        st.stop()

st.subheader("Propuestas de entrada")
st.caption(f"Origen detectado: {source_label}. Se excluyen los campos sensibles de la comparacion.")
st.dataframe(proposals, use_container_width=True, hide_index=True)
st.download_button("Descargar plantilla de ejemplo", csv_bytes(sample_proposals()), "propuestas_ejemplo.csv", "text/csv")

try:
    config = DetectionConfig(
        lexical_weight=lexical_weight,
        jaccard_weight=jaccard_weight,
        semantic_weight=semantic_weight,
        duplicate_threshold=duplicate_threshold,
        review_threshold=review_threshold,
        block_by_axis=block_by_axis,
    )
    encoder = load_semantic_encoder() if use_semantic_model else None
    with st.spinner("Comparando propuestas por municipio y eje..."):
        pairs = find_duplicate_pairs(proposals, config, encoder)
except Exception as error:
    st.error(str(error))
    st.stop()

summary = detection_summary(pairs)
metric_a, metric_b, metric_c = st.columns(3)
metric_a.metric("Parejas evaluadas", summary["parejas_evaluadas"])
metric_b.metric("Posibles duplicados", summary["posibles_duplicados"])
metric_c.metric("Para revision", summary["para_revision"])

st.subheader("Casos que requieren atencion")
alerts = pairs[pairs["estado"] != "sin_alerta"].copy()
if alerts.empty:
    st.success("No se encontraron parejas que superen el umbral de revision.")
else:
    visible_columns = [
        "estado", "puntaje_final", "coseno_lexico", "jaccard_fragmentos", "coseno_semantico",
        "municipality", "axis", "proposal_id_a", "proposal_a", "proposal_id_b", "proposal_b",
    ]
    st.dataframe(
        alerts[visible_columns].style.format(
            {"coseno_lexico": "{:.2f}", "jaccard_fragmentos": "{:.2f}", "coseno_semantico": "{:.2f}", "puntaje_final": "{:.2f}"}
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.download_button("Descargar casos para revision", csv_bytes(alerts), "casos_revision.csv", "text/csv")

with st.expander("Ver todas las parejas comparadas"):
    st.dataframe(pairs, use_container_width=True, hide_index=True)

st.markdown(
    """
**Columnas requeridas:** `proposal_id`, `municipality`, `axis`, `proposal`.
`expected_result` es opcional y se suma al texto para comparar cuando existe.

La herramienta usa coseno de bolsas de palabras, Jaccard sobre fragmentos de cinco caracteres y, si se activa, coseno de embeddings. Calibre pesos y umbrales con una muestra revisada manualmente antes de una decision operativa.
"""
)
