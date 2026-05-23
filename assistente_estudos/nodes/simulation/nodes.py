"""Os nós do workflow de simulação adaptativa.

Fluxo:
    preparar_simulacao → executar_simulacao → avaliar_resultado → persistir_simulacao
"""

from __future__ import annotations

from assistente_estudos.nodes.simulation.state import SimulationState


def preparar_simulacao_node(state: SimulationState) -> SimulationState:
    """Gera as questões do simulado adaptadas ao plano e nível do usuário.

    TODO: usar LLM para gerar questões por tópico com dificuldade adequada.
    """
    return state


def executar_simulacao_node(state: SimulationState) -> SimulationState:
    """Processa as respostas do usuário e ajusta a dificuldade dinamicamente.

    TODO: aplicar lógica adaptativa — aumentar/reduzir dificuldade por acerto/erro.
    """
    return state


def avaliar_resultado_node(state: SimulationState) -> SimulationState:
    """Calcula a taxa de acerto por tópico e consolida simulation_output.

    TODO: agrupar resultados por disciplina/tópico e calcular métricas.
    """
    return state


def persistir_simulacao_node(state: SimulationState) -> SimulationState:
    """Salva o resultado do simulado no banco.

    TODO: gravar em resultados_simulados e atualizar state["simulado_id"].
    """
    return state
