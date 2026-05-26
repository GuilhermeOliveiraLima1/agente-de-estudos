"""Serviço de integração com LLaMA via Ollama.

Este módulo será responsável, no futuro, por encapsular chamadas ao modelo,
mantendo o restante da aplicação independente do provedor.
"""

import os
from langchain_ollama import ChatOllama


def get_llm(temperature: float = 0.3) -> ChatOllama:
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.2:1b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=temperature,
    )


# Instância padrão reutilizável
llm = get_llm()
