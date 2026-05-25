"""Tools disponíveis para o workflow de relatório."""

from __future__ import annotations

from statistics import mean
from typing import List

from langchain_core.tools import tool


@tool
def calcular_media_notas(notas: List[float]) -> str:
    """
    Calcula a média geral das notas do aluno.
    """

    if not notas:
        return "Nenhuma nota encontrada."

    media = round(mean(notas), 2)

    if media >= 7:
        status = "bom desempenho"
    elif media >= 5:
        status = "desempenho mediano"
    else:
        status = "baixo desempenho"

    return (
        f"Média calculada: {media}. "
        f"O aluno possui {status}."
    )


@tool
def analisar_frequencia(frequencia: float) -> str:
    """
    Analisa a frequência do aluno.
    """

    if frequencia >= 75:
        return (
            f"Frequência de {frequencia}%: "
            "frequência adequada."
        )

    return (
        f"Frequência de {frequencia}%: "
        "frequência abaixo do recomendado."
    )


@tool
def gerar_recomendacoes(media: float) -> str:
    """
    Gera recomendações de estudo com base na média.
    """

    if media >= 8:
        return (
            "Aluno apresenta ótimo desempenho. "
            "Recomenda-se aprofundamento em conteúdos avançados."
        )

    if media >= 6:
        return (
            "Aluno possui desempenho razoável. "
            "Recomenda-se reforço semanal e resolução de exercícios."
        )

    return (
        "Aluno apresenta dificuldades. "
        "Recomenda-se plano intensivo de estudos e revisões diárias."
    )


@tool
def formatar_relatorio(texto: str) -> str:
    """
    Formata o texto do relatório.
    """

    return (
        "===== RELATÓRIO EDUCACIONAL =====\n\n"
        f"{texto}\n\n"
        "===== FIM DO RELATÓRIO ====="
    )


TOOLS = [
    calcular_media_notas,
    analisar_frequencia,
    gerar_recomendacoes,
    formatar_relatorio,
]