# Assistente de Planejamento de Estudos Inteligente

Projeto em Python preparado para evoluir para um assistente de estudos com LangGraph, integração futura a LLaMA via Ollama, persistência em banco e interface web.

Esta versão contém apenas a estrutura arquitetural inicial. Não há lógica de negócio implementada ainda.

## Objetivo

Organizar o sistema em camadas bem definidas para permitir crescimento sem acoplamento excessivo:

- interface web
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
├── services/
│   ├── llm_service.py
│   └── persistence_service.py
└── web/
    ├── app.py
    ├── routes.py
    ├── dependencies.py
    ├── templates/
    └── static/
```

## Como o fluxo funciona

O ponto de entrada da aplicação é [assistente_estudos/main.py](assistente_estudos/main.py). Ele inicializa o grafo e prepara a aplicação web. Nesta base inicial, a execução ainda não processa dados de fato, mas o caminho já está separado para crescer de forma limpa.

O grafo é montado em [assistente_estudos/core/graph_builder.py](assistente_estudos/core/graph_builder.py). Esse arquivo registra os nós do fluxo no LangGraph e concentra a orquestração de alto nível.

O estado compartilhado entre as etapas fica em [assistente_estudos/core/state.py](assistente_estudos/core/state.py), usando `StudyState` com `TypedDict`. É aqui que ficam os campos que representam dados do aluno, cronograma, simulações, análises, relatórios e metadados.

Os nós do fluxo estão em [assistente_estudos/nodes](assistente_estudos/nodes). Cada arquivo representa uma etapa específica:

- `planner_node.py`: cria o cronograma inicial a partir das entradas e dados salvos.
- `replan_node.py`: recalcula o cronograma com base no que foi ou não estudado.
- `simulation_node.py`: executa o simulado adaptativo e ajusta a dificuldade.
- `analysis_node.py`: analisa resultados e destaca pontos que exigem atenção.
- `report_node.py`: consolida a saída final para relatório/exportação.

Os serviços ficam em [assistente_estudos/services](assistente_estudos/services). Eles existem para isolar detalhes técnicos:

- `llm_service.py`: integração futura com Ollama/LLaMA.
- `persistence_service.py`: persistência em banco ou outro armazenamento.

A interface web fica em [assistente_estudos/web](assistente_estudos/web), separando a apresentação da lógica de orquestração:

- `app.py`: cria a aplicação web.
- `routes.py`: define as rotas e páginas da interface.
- `dependencies.py`: concentra dependências compartilhadas da camada web.
- `templates/`: arquivos HTML renderizados pela interface.
- `static/`: CSS, JavaScript e imagens.

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
- `jinja2`

## Execução futura

Quando a implementação começar, o fluxo esperado será:

1. o usuário acessa a interface web
2. a rota web coleta os dados do formulário
3. o estado inicial é montado
4. o grafo LangGraph coordena os nós
5. os serviços consultam/persistem dados
6. o relatório final é gerado e exibido/exportado

## Observação

Este repositório está somente com a base estrutural. Todas as funções e classes foram deixadas sem lógica propositalmente para servir como fundação da implementação posterior.
