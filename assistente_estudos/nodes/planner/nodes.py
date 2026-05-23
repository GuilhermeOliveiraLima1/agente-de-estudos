"""Os nós do workflow de planejamento inicial.

Fluxo:
    coletar_preferencias → gerar_cronograma → validar_cronograma → persistir_cronograma
"""

from __future__ import annotations

from assistente_estudos.nodes.planner.state import PlannerState


def coletar_preferencias_node(state: PlannerState) -> PlannerState:
    """Lê e normaliza as preferências e restrições do usuário.

    TODO: buscar dados complementares do banco (histórico, disciplinas).
    """
    return state


def gerar_cronograma_node(state: PlannerState) -> PlannerState:
    """Gera o cronograma inicial com base nas preferências coletadas.

    TODO: invocar LLM ou algoritmo de distribuição de carga horária.
    """
    return state


def validar_cronograma_node(state: PlannerState) -> PlannerState:
    """Verifica se o cronograma gerado respeita as restrições do usuário.

    TODO: checar conflitos de horário, carga máxima por dia, prioridades.
    """
    return state


def persistir_cronograma_node(state: PlannerState) -> PlannerState:
    """Salva o cronograma no banco e retorna o ID do registro.

    TODO: gravar em tabela de cronogramas e atualizar state["plano_id"].
    """
    return state
