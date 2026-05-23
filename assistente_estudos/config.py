"""Configurações centrais do Assistente de Planejamento de Estudos Inteligente.

Este módulo reúne parâmetros de execução, integração futura com Ollama e
constantes de organização do projeto.
"""

from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = DATA_DIR / "exports"
STATES_DIR = DATA_DIR / "states"
APP_TITLE = "Assistente de Planejamento de Estudos Inteligente"
API_PREFIX = "/api"
API_HOST = "127.0.0.1"
API_PORT = 8000
OLLAMA_MODEL = "llama3:8b"
OLLAMA_BASE_URL = "http://localhost:11434"
