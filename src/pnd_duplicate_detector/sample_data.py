"""Synthetic examples safe for demonstration."""

from __future__ import annotations

import pandas as pd


def sample_proposals() -> pd.DataFrame:
    rows = [
        ("P-001", "Almeida", "Infraestructura", "Arreglar las vias veredales y los puentes de Almeida", "Mejorar la conectividad rural a 2030"),
        ("P-002", "Almeida", "Infraestructura", "Mejorar las vias y puentes veredales en Almeida", "Mejorar la conectividad rural a 2030"),
        ("P-003", "Almeida", "Infraestructura", "Arreglar vias veredlales y puentes de Almeida", "Mejorar la conectividad rural a 2030"),
        ("P-004", "Sogamoso", "Infraestructura", "Arreglar las vias veredales y los puentes de Almeida", "Mejorar la conectividad rural a 2030"),
        ("P-005", "Almeida", "Servicios publicos", "Instalar luminarias solares en parques municipales", "Aumentar la seguridad en espacios publicos"),
        ("P-006", "Almeida", "Servicios publicos", "Poner alumbrado solar en parques publicos", "Aumentar la seguridad en espacios publicos"),
        ("P-007", "Almeida", "Salud", "Dotar el centro de salud con equipos de atencion materna", "Reducir la mortalidad materna"),
        ("P-008", "Almeida", "Salud", "Construir una cancha cubierta para jovenes", "Incrementar la actividad fisica"),
    ]
    return pd.DataFrame(rows, columns=["proposal_id", "municipality", "axis", "proposal", "expected_result"])
