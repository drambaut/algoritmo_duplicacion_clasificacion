import pandas as pd

from pnd_duplicate_detector.input_adapter import adapt_input


def test_adapts_consulta_layout() -> None:
    source = pd.DataFrame(
        {
            "id_propuesta": ["10"],
            "p_propuesta": ["Mejorar vias rurales"],
            "p_mcpio_nombre": ["Almeida"],
            "eje_vigente": ["Infraestructura"],
            "p_resultado": ["Mayor conectividad"],
        }
    )
    result = adapt_input(source)
    assert result.source_format == "Hoja Consulta"
    assert result.proposals.loc[0, "municipality"] == "Almeida"
    assert result.proposals.loc[0, "expected_result"] == "Mayor conectividad"


def test_adapts_corte_layout_to_one_row_per_proposal() -> None:
    source = pd.DataFrame(
        {
            "radicado": [101],
            "eje1_tema": ["Infraestructura"],
            "eje1_propuesta": ["Arreglar puentes rurales"],
            "eje1_dpto": [15],
            "eje1_mcpio": [22],
            "eje1_resultado": ["Mayor conectividad"],
            "eje2_propuesta": [""],
        }
    )
    result = adapt_input(source)
    proposal = result.proposals.loc[0]
    assert result.source_format == "Hoja corte"
    assert proposal.proposal_id == "101::bloque_1"
    assert proposal.municipality == "15-22"
    assert proposal.axis == "bloque_1"
