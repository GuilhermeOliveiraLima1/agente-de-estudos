"""Estado tipado exclusivo do workflow de planejamento inicial."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class PlannerState(TypedDict, total=False):
    # --- Entrada (preenchida pela rota antes de invocar o grafo) ---
    usuario_id: str
    study_goal: str
    subjects: List[str]
    priority_subjects: List[str]
    available_time_hours: float
    study_days_per_week: int
    learning_preferences: Dict[str, Any]
    constraints: Dict[str, Any]

    # --- Saída (preenchida pelos nós) ---
    current_plan: Dict[str, Any]   # cronograma gerado
    plano_id: str                  # ID do registro salvo no banco

    # Erro, se houver
    erro: Optional[str]
