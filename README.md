# Assistente de Planejamento de Estudos Inteligente

Projeto em Python preparado para evoluir para um assistente de estudos com LangGraph, integração futura a LLaMA via Ollama, persistência em banco e API para consumo por um frontend separado.

Esta versão contém apenas a estrutura arquitetural inicial. Não há interface web neste repositório.

## Objetivo

Organizar o sistema em camadas bem definidas para permitir crescimento sem acoplamento excessivo:

- API JSON para consumo externo
- orquestração com LangGraph
- nós separados por responsabilidade
- estado tipado compartilhado entre etapas
- serviços de persistência e LLM
- configuração centralizada
- geração futura de relatórios e exportações

## Estrutura

```text
assistente_estudos/
├── main.py
├── config.py
├── core/
│   ├── state.py
│   └── graph_builder.py
├── nodes/
│   ├── planner_node.py
│   ├── replan_node.py
│   ├── simulation_node.py
│   ├── analysis_node.py
│   └── report_node.py
├── api/
│   ├── app.py
│   ├── routes.py
│   ├── schemas.py
│   └── dependencies.py
└── services/
    ├── agent_service.py
    ├── llm_service.py
    └── persistence_service.py
```

## Como o fluxo funciona

O ponto de entrada da aplicação é [assistente_estudos/main.py](assistente_estudos/main.py). Ele expõe a aplicação FastAPI da API e mantém a base pronta para ser consumida por outro frontend. Nesta fase, a API já devolve contratos JSON estruturados, mas a lógica dos agentes ainda está em fase estrutural.

O grafo é montado em [assistente_estudos/core/graph_builder.py](assistente_estudos/core/graph_builder.py). Esse arquivo registra os nós do fluxo no LangGraph e concentra a orquestração de alto nível.

O estado compartilhado entre as etapas fica em [assistente_estudos/core/state.py](assistente_estudos/core/state.py), usando `StudyState` com `TypedDict`. É aqui que ficam os campos que representam dados do aluno, cronograma, simulações, análises, relatórios e metadados.

Os nós do fluxo estão em [assistente_estudos/nodes](assistente_estudos/nodes). Cada arquivo representa uma etapa específica:

- `planner_node.py`: cria o cronograma inicial a partir das entradas e dados salvos.
- `replan_node.py`: recalcula o cronograma com base no que foi ou não estudado.
- `simulation_node.py`: executa o simulado adaptativo e ajusta a dificuldade.
- `analysis_node.py`: analisa resultados e destaca pontos que exigem atenção.
- `report_node.py`: consolida a saída final para relatório/exportação.

Os serviços ficam em [assistente_estudos/services](assistente_estudos/services). Eles existem para isolar detalhes técnicos:

- `agent_service.py`: fronteira da API para os fluxos de agentes.
- `llm_service.py`: integração futura com Ollama/LLaMA.
- `persistence_service.py`: persistência em banco ou outro armazenamento.

A camada HTTP fica em [assistente_estudos/api](assistente_estudos/api), separando os contratos JSON da lógica de orquestração:

- `app.py`: cria a aplicação FastAPI.
- `routes.py`: define as rotas JSON da API.
- `schemas.py`: contratos de entrada e saída.
- `dependencies.py`: concentra dependências compartilhadas da API.

## Como criar um novo agente

Para adicionar um novo agente, siga esta ordem:

1. Crie um nó em [assistente_estudos/nodes](assistente_estudos/nodes) seguindo o padrão dos arquivos existentes.
2. Registre esse nó em [assistente_estudos/core/graph_builder.py](assistente_estudos/core/graph_builder.py) para mantê-lo disponível na orquestração.
3. Exponha a etapa em [assistente_estudos/services/agent_service.py](assistente_estudos/services/agent_service.py), adicionando o nome do agente na lista interna e o comportamento estrutural correspondente.
4. Se o payload ou a resposta mudarem, atualize os schemas em [assistente_estudos/api/schemas.py](assistente_estudos/api/schemas.py).
5. Crie ou ajuste a rota em [assistente_estudos/api/routes.py](assistente_estudos/api/routes.py) para publicar o novo endpoint JSON.

Padrão recomendado para cada agente:

- um arquivo por responsabilidade em `nodes/`
- uma única etapa exposta por vez na API
- entrada e saída tipadas via Pydantic quando houver contrato novo
- lógica de orquestração centralizada em `agent_service.py`

### Local dos agentes

Criamos uma pasta dedicada para agentes em [assistente_estudos/agents](assistente_estudos/agents). Ela contém templates:

- `planner_agent.py`
- `replan_agent.py`
- `simulation_agent.py`
- `analysis_agent.py`
- `report_agent.py`

Cada arquivo é um template que chama o respectivo nó em `assistente_estudos/nodes`. Você pode editar esses templates para implementar a lógica do agente, ou substituir por implementações mais completas.

## Como usar a API

O backend expõe a aplicação FastAPI com prefixo `/api`.

Endpoints principais:

- `GET /api/health`: verifica se o serviço está no ar.
- `GET /api/agents`: lista os agentes disponíveis.
- `POST /api/agents/planner`: executa a etapa de planejamento.
- `POST /api/agents/replan`: executa a etapa de replanejamento.
- `POST /api/agents/simulation`: executa a etapa de simulação.
- `POST /api/agents/analysis`: executa a etapa de análise.
- `POST /api/agents/report`: executa a etapa de relatório.
- `POST /api/agents/pipeline`: executa o fluxo completo.

Exemplo de uso com `curl`:

```bash
curl -X POST http://127.0.0.1:8000/api/agents/planner \
    -H "Content-Type: application/json" \
    -d "{\"user_name\": \"Ana\", \"study_goal\": \"Concurso\", \"subjects\": [\"Matemática\", \"Português\"]}"
```

Resposta esperada na fase atual:

- `status`: retorna `structural`
- `message`: indica que a estrutura da API está pronta
- `state`: devolve o payload recebido com metadados atualizados

## Fluxos planejados

O projeto foi pensado para suportar cinco fluxos principais:

1. Gerar cronograma com base nas entradas salvas no banco e exportar PDF ou TXT.
2. Recalcular o cronograma verificando o que foi ou não estudado e registrar o que mudou.
3. Rodar simulados adaptativos, ajustando o nível conforme o desempenho.
4. Gerar relatório a partir dos resultados dos simulados, destacando tópicos com maior necessidade de revisão.
5. Exportar tudo em PDF ou TXT em uma visão consolidada.

## Persistência

A estrutura já comporta armazenamento em banco de dados. O serviço de persistência foi criado para que a aplicação possa começar com SQLite e depois migrar para PostgreSQL ou outra solução sem mudar toda a arquitetura.

Os dados que fazem sentido persistir incluem:

- dados do aluno
- cronograma atual
- histórico de estudo
- respostas de simulados
- replanejamentos
- relatórios gerados
- metadados de sessão

## Dependências

As dependências principais estão em [requirements.txt](requirements.txt):

- `langgraph`
- `langchain`
- `langchain-ollama`
- `ollama`
- `pydantic`
- `fastapi`
- `uvicorn`

## Execução futura

Quando a implementação começar, o fluxo esperado será:

1. o frontend externo envia os dados para a API
2. a rota JSON valida o payload e monta o estado inicial
3. o grafo LangGraph coordena os nós
4. os serviços consultam/persistem dados
5. a resposta final é devolvida para o frontend exibir/exportar

## Como rodar a API

Use o `uvicorn` apontando para o `main.py` da raiz:

```bash
uvicorn main:app --reload
```

Se quiser mudar host ou porta, ajuste [assistente_estudos/config.py](assistente_estudos/config.py).

## Instalação (passo a passo)

Recomendo usar um ambiente virtual. As instruções abaixo são para Windows (PowerShell) e uma alternativa genérica POSIX.

1. Crie e ative um ambiente virtual (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Alternativa POSIX (macOS / Linux):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instale dependências:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Rode a API em desenvolvimento:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

4. Teste rapidamente (exemplo):

```bash
curl -X GET http://127.0.0.1:8000/api/health
```

5. (Opcional) Se ambientes virtuais ou caches foram acidentalmente versionados, remova-os do índice do git e atualize o `.gitignore` assim:

```bash
# adicionar entradas ao .gitignore (se ainda não estiverem lá)
echo ".venv/" >> .gitignore
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore

# remover do índice sem apagar localmente
git rm -r --cached .venv venv "__pycache__" || true
git commit -m "Remove ambientes virtuais e caches do repositório"
```

Observação: `python` deve ser uma versão compatível (3.10+ recomendada). Ajuste os comandos conforme sua shell preferida.

## Observação

Este repositório está somente com a base estrutural. A camada web foi removida para manter apenas a API de backend consumida por outro projeto de frontend.
