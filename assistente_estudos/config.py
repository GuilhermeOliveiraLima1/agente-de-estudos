"""Configurações centrais do Assistente de Planejamento de Estudos Inteligente.

Este módulo reúne parâmetros de execução, integração futura com Ollama e
constantes de organização do projeto.
"""

from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OLLAMA_MODEL = "llama3:8b"
OLLAMA_BASE_URL = "http://localhost:11434"
WEB_HOST = "127.0.0.1"
WEB_PORT = 8000
TEMPLATE_DIR = BASE_DIR / "web" / "templates"
STATIC_DIR = BASE_DIR / "web" / "static"
