"""Os nós do workflow de geração de relatório.

Fluxo:
    coletar_dados → gerar_relatorio → exportar_relatorio → persistir_relatorio
"""

from __future__ import annotations

from assistente_estudos.nodes.report.state import ReportState


def coletar_dados_node(state: ReportState) -> ReportState:
    """Consolida os dados de análise, simulados e cronograma em report_data.

    TODO: agregar analysis_output + simulation_output + current_plan em uma
          estrutura única pronta para ser narrada pelo LLM.
    """
    return state


def gerar_relatorio_node(state: ReportState) -> ReportState:
    """Invoca o LLM para gerar o texto narrativo do relatório.

    TODO: montar prompt com report_data e pedir ao LLM um relatório
          com seções: resumo, desempenho, pontos de melhoria e próximos passos.
    """
    return state


def exportar_relatorio_node(state: ReportState) -> ReportState:
    """Exporta o relatório para PDF ou TXT e registra o caminho em export_path.

    TODO: usar biblioteca de geração de PDF (ex: reportlab, weasyprint)
          ou simplesmente gravar um .txt em EXPORTS_DIR do config.
    """
    return state


def persistir_relatorio_node(state: ReportState) -> ReportState:
    """Salva o relatório gerado no banco e retorna o ID do registro.

    TODO: gravar report_text e export_path no banco; atualizar state["relatorio_id"].
    """
    return state
