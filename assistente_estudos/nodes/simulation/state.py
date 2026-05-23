"""Estado tipado exclusivo do workflow de simulação."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class SimulationState(TypedDict, total=False):
    # --- Entrada ---
    usuario_id: str
    current_plan: Dict[str, Any]     # cronograma a ser simulado
    nivel_dificuldade: str           # basico | intermediario | avancado

    # --- Saída ---
    questoes: List[Dict[str, Any]]   # questões geradas pelo simulado
    respostas: List[Dict[str, Any]]  # respostas do usuário
    simulation_output: Dict[str, Any]  # resultado consolidado
    simulado_id: str                 # ID do registro salvo no banco

    # Erro, se houver
    erro: Optional[str]
