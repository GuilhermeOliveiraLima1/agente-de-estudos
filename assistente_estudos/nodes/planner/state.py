"""Estado tipado exclusivo do workflow de planejamento inicial."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class PlannerState(TypedDict, total=False):
    # --- Entrada ---
    usuario_id: str
    discipline: str
    subject: str
    level: str
    exam_date: str
    hours_per_day: int

    # --- Saída ---
    topics: List[Any]
    study_plan: List[Any]
    plan_summary: Dict[str, Any]

    erro: Optional[str]
