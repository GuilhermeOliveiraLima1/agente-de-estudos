"""Estado tipado exclusivo do workflow de replanejamento."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class ReplanState(TypedDict, total=False):
    # --- Entrada ---
    usuario_id: str
    current_plan: Dict[str, Any]      # cronograma atual
    replanning_reason: str            # motivo do replanejamento
    sessoes_realizadas: List[Dict]    # o que foi de fato estudado
    constraints: Dict[str, Any]

    # --- Saída ---
    updated_plan: Dict[str, Any]      # novo cronograma
    desvios: List[str]                # lista de desvios identificados
    replan_id: str                    # ID do registro salvo no banco

    # Erro, se houver
    erro: Optional[str]
