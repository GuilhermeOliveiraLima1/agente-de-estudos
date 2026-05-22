"""Serviço de integração com LLaMA via Ollama.

Este módulo será responsável, no futuro, por encapsular chamadas ao modelo,
mantendo o restante da aplicação independente do provedor.
"""

from __future__ import annotations


class LLMService:
    """Interface estrutural para o provedor de linguagem."""

    def __init__(self) -> None:
        """Inicializa a camada de serviço de linguagem."""

        pass

    def generate(self, prompt: str) -> str:
        """Gera uma resposta textual para um prompt recebido."""

        pass
