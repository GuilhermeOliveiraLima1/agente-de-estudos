"""Tools disponíveis para o LLM durante a geração do parecer.

Estas funções são expostas como ferramentas que o modelo pode chamar
para enriquecer o parecer com cálculos adicionais sobre o desempenho.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from langchain_core.tools import tool


@tool
def calcular_media_por_topico(resultados: List[dict]) -> Dict[str, float]:
    """Calcula a média de taxa de acerto agrupada por tópico.

    Use esta ferramenta quando quiser saber o desempenho médio do estudante
    em cada tópico específico antes de redigir o parecer.
    """
    agrupado: Dict[str, List[float]] = defaultdict(list)
    for r in resultados:
        agrupado[r["topico"]].append(r["taxa_acerto"])
    return {
        topico: round(sum(taxas) / len(taxas), 3)
        for topico, taxas in agrupado.items()
    }


@tool
def detectar_tendencia_semanal(scores_historicos: List[float]) -> str:
    """Analisa a sequência de scores e retorna a tendência de evolução.

    Retorna 'melhorando', 'estavel' ou 'piorando'. Use esta ferramenta
    para embasar comentários sobre progresso ao longo do tempo.
    """
    if len(scores_historicos) < 2:
        return "sem_historico_suficiente"
    diferenca = scores_historicos[-1] - scores_historicos[0]
    if diferenca > 5:
        return "melhorando"
    if diferenca < -5:
        return "piorando"
    return "estavel"


@tool
def identificar_topicos_criticos(
    medias_por_topico: Dict[str, float],
    limiar: float = 0.6,
) -> List[str]:
    """Retorna os tópicos com média de acerto abaixo do limiar indicado.

    Use esta ferramenta para listar os tópicos que precisam de reforço
    antes de redigir recomendações concretas no parecer.
    """
    return [
        topico
        for topico, media in medias_por_topico.items()
        if media < limiar
    ]


TOOLS = [calcular_media_por_topico, detectar_tendencia_semanal, identificar_topicos_criticos]
