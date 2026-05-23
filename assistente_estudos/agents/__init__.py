"""Pacote de agentes.

Cada agente deve expor uma função `run(state: dict) -> dict` que recebe o
estado atual e retorna o estado atualizado. Os arquivos de nó em
`assistente_estudos/nodes` armazenam a lógica por responsabilidade; os
agentes podem orquestrar chamadas entre eles, serviços e persistência.
"""

from .planner_agent import run as planner
from .replan_agent import run as replan
from .simulation_agent import run as simulation
from .analysis_agent import run as analysis
from .report_agent import run as report

__all__ = ["planner", "replan", "simulation", "analysis", "report"]
