"""Os nós do workflow de replanejamento.

Fluxo:
    analisar_desvio → recalcular_cronograma → persistir_replanejamento
"""

from __future__ import annotations

from assistente_estudos.nodes.replan.state import ReplanState


def analisar_desvio_node(state: ReplanState) -> ReplanState:
    """Compara o plano original com o que foi realizado e lista os desvios.

    TODO: buscar sessões realizadas no banco e comparar com current_plan.
    """
    return state


def recalcular_cronograma_node(state: ReplanState) -> ReplanState:
    """Gera um novo cronograma ajustado com base nos desvios identificados.

    TODO: invocar LLM ou redistribuir carga considerando o que ficou para trás.
    """
    return state


def persistir_replanejamento_node(state: ReplanState) -> ReplanState:
    """Salva o novo cronograma e o registro de replanejamento no banco.

    TODO: gravar updated_plan e log de replanejamento; atualizar state["replan_id"].
    """
    return state
