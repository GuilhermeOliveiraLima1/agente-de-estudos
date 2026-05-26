"""Ponte entre o grafo principal e o sub-grafo de análise de desempenho."""

from __future__ import annotations

from assistente_estudos.core.state import StudyState


def analysis_node(state: StudyState) -> StudyState:
    """Executa o workflow completo de análise de desempenho."""
    from assistente_estudos.nodes.analysis.graph import build_analysis_graph

    usuario_id = state.get("usuario_id") or state.get("session_id")
    if not usuario_id:
        return {**state, "error_message": "usuario_id ausente: não é possível executar a análise."}

    graph = build_analysis_graph()
    resultado = graph.invoke({"usuario_id": usuario_id, "periodo_dias": 30})

    return {
        **state,
        "analysis_output": {
            "indice_prontidao": resultado.get("indice_prontidao"),
            "classificacao": resultado.get("classificacao"),
            "score_dominio": resultado.get("score_dominio"),
            "score_consistencia": resultado.get("score_consistencia"),
            "score_retencao": resultado.get("score_retencao"),
            "topicos_frageis": resultado.get("topicos_frageis"),
            "tendencia": resultado.get("tendencia"),
            "parecer_llm": resultado.get("parecer_llm"),
            "resultado_id": resultado.get("resultado_id"),
        },
    }
