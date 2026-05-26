"""Estado tipado exclusivo do workflow de replanejamento."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class ReplanState(TypedDict, total=False):
    # --- Entrada ---
    usuario_id: str
    current_plan: Dict[str, Any]      # cronograma atual
    replanning_reason: str            # motivo do replanejamento
    sessoes_realizadas: List[Dict]    # o que foi de fato estudado
    resultados_simulados: List[Dict]   # resultados de simulados realizados
    constraints: Dict[str, Any]

    desvios: List[Dict[str, Any]]

    # --- Saída ---
    updated_plan: Dict[str, Any]      # novo cronograma
    replan_id: str                    # ID do registro salvo no banco

    # Erro, se houver
    erro: Optional[str]
