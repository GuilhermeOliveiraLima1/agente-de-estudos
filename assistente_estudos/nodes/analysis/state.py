"""Estado tipado exclusivo do workflow de análise de desempenho."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class AnalysisState(TypedDict, total=False):
    # Entrada
    usuario_id: str
    periodo_dias: int

    # Dados coletados do banco
    sessoes: List[Dict[str, Any]]
    resultados_simulados: List[Dict[str, Any]]

    # Scores calculados
    score_dominio: float
    score_consistencia: float
    score_retencao: float

    # Resultado final
    indice_prontidao: float
    classificacao: str          # risco_alto | moderado | alta_probabilidade
    topicos_frageis: List[str]
    tendencia: str              # melhorando | estavel | piorando

    # Parecer gerado pelo LLM
    parecer_llm: str

    # ID do registro salvo no banco
    resultado_id: str

    # Erro, se houver
    erro: Optional[str]
