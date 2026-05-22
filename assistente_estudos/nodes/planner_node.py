"""Nó responsável pela criação inicial do plano de estudos.

O objetivo deste módulo é concentrar a etapa de planejamento inicial sem
acoplar regras de negócio nesta base estrutural.
"""

from __future__ import annotations

from assistente_estudos.core.state import StudyState


def planner_node(state: StudyState) -> StudyState:
    """Define o ponto de entrada do planejamento inicial."""

    pass
