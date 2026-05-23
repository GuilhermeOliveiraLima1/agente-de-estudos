# 🎓 Assistente de Planejamento de Estudos Inteligente

Sistema backend que ajuda estudantes a organizar, acompanhar e analisar seus estudos. Ele é dividido em **agentes** — cada um responsável por uma tarefa específica, como criar um cronograma, rodar um simulado ou gerar um relatório.

> Este repositório é só o **servidor (backend)**. O aplicativo visual (frontend) é um projeto separado que conversa com ele via API.

---

## 📋 Sumário

- [Tecnologias usadas](#-tecnologias-usadas)
- [Como o sistema é organizado](#-como-o-sistema-é-organizado)
- [Mapa de pastas](#-mapa-de-pastas)
- [Como funciona por dentro](#-como-funciona-por-dentro)
- [Como desenvolver seu agente](#-como-desenvolver-seu-agente)
- [Rotas disponíveis na API](#-rotas-disponíveis-na-api)
- [Banco de dados](#-banco-de-dados)
- [Subindo com Docker](#-subindo-com-docker)
- [Rodando sem Docker](#-rodando-sem-docker)
- [Dependências](#-dependências)

---

## 🛠 Tecnologias usadas

Não precisa dominar tudo isso para contribuir — mas é bom saber o que cada peça faz:

| Tecnologia | O que faz neste projeto |
|---|---|
| **FastAPI** | Recebe as requisições HTTP e devolve respostas JSON |
| **LangGraph** | Controla a ordem de execução dos agentes (como um fluxograma em código) |
| **SQLAlchemy** | Salva e busca dados no banco sem precisar escrever SQL |
| **PostgreSQL** | O banco de dados onde tudo é armazenado |
| **Ollama / LLaMA** | Modelo de inteligência artificial rodando localmente na sua máquina |
| **Pydantic** | Garante que os dados que chegam e saem da API estão no formato correto |
| **Docker** | Empacota tudo (banco, IA, servidor) para rodar igual em qualquer computador |

---

## 🏗 Como o sistema é organizado

O sistema tem três camadas que trabalham em sequência:

```
Aplicativo do estudante
        │  envia dados via HTTP
        ▼
┌─────────────┐
│   api/      │  Recebe o pedido e repassa para o agente correto
└──────┬──────┘
       │
┌──────▼──────┐
│   nodes/    │  O agente processa os dados e executa a lógica
└──────┬──────┘
       │
┌──────▼──────┐
│    db/      │  Salva ou busca informações no banco de dados
└─────────────┘
```

Cada agente vive em uma pasta própria dentro de `nodes/` e pode ter vários passos internos (chamados de **nós**). O arquivo `*_node.py` é a "porta de entrada" do agente — ele conecta o sistema com os passos internos.

---

## 📁 Mapa de pastas

```text
agente-de-estudos/
├── main.py                        # Liga o servidor e cria as tabelas no banco ao iniciar
├── Dockerfile                     # Receita para montar o container do servidor
├── docker-compose.yml             # Sobe banco + IA + servidor com um único comando
├── requirements.txt               # Lista de bibliotecas Python necessárias
├── .env.example                   # Exemplo de configurações — copie para .env
│
└── assistente_estudos/
    ├── config.py                  # Configurações gerais (portas, URLs, nomes)
    │
    ├── core/
    │   ├── state.py               # Define quais dados circulam entre os agentes
    │   └── graph_builder.py       # Registra todos os agentes no sistema
    │
    ├── db/
    │   ├── database.py            # Abre e fecha a conexão com o banco
    │   └── models.py              # Define as tabelas do banco como classes Python
    │
    ├── nodes/                     # Cada pasta aqui = um agente do sistema
    │   │
    │   ├── planner_node.py        # Porta de entrada do agente de planejamento
    │   ├── planner/               # 👈 Passos internos do planejamento (você implementa aqui)
    │   │   ├── state.py           #    Dados que este agente usa e produz
    │   │   ├── graph.py           #    Ordem dos passos já definida
    │   │   ├── nodes.py           #    Funções de cada passo (com TODO para preencher)
    │   │   └── tools.py           #    Funções extras que a IA pode usar
    │   │
    │   ├── replan_node.py         # Porta de entrada do agente de replanejamento
    │   ├── replan/                # 👈 Passos internos do replanejamento
    │   │   └── ...
    │   │
    │   ├── simulation_node.py     # Porta de entrada do agente de simulação
    │   ├── simulation/            # 👈 Passos internos da simulação
    │   │   └── ...
    │   │
    │   ├── analysis_node.py       # Porta de entrada do agente de análise
    │   ├── analysis/              # ✅ Análise de desempenho (já implementada)
    │   │   └── ...
    │   │
    │   ├── report_node.py         # Porta de entrada do agente de relatório
    │   └── report/                # 👈 Passos internos do relatório
    │       └── ...
    │
    ├── services/
    │   ├── llm_service.py         # Comunicação com o modelo de IA (Ollama)
    │   └── persistence_service.py # Operações de banco mais complexas (para usar no futuro)
    │
    └── api/
        ├── app.py                 # Cria o servidor FastAPI
        ├── routes.py              # Define todas as rotas (URLs que a API responde)
        ├── schemas.py             # Formatos esperados de entrada e saída
        └── dependencies.py        # Compartilha a conexão com o banco entre as rotas
```

---

## ⚙️ Como funciona por dentro

### Na hora de ligar o servidor

Quando o servidor sobe, `main.py` cria automaticamente todas as tabelas no banco que ainda não existem. Ou seja, **não precisa criar tabelas na mão** — o próprio código faz isso.

### Caminho de uma requisição

Exemplo: o frontend pede para criar um cronograma.

```
POST /api/agentes/planner
  │
  ├─ api/routes.py      verifica se os dados chegaram no formato correto
  │
  ├─ planner_node.py    passa os dados para os passos internos do agente
  │
  ├─ planner/graph.py   executa os passos em ordem:
  │                     coletar preferências → gerar cronograma → validar → salvar
  │
  └─ api/routes.py      devolve o resultado para o frontend
```

### O "estado" que passa entre os agentes

Pense no estado como uma **mochila de dados**. Cada agente pega a mochila, coloca o que produziu dentro, e passa para o próximo. O `StudyState` (em `core/state.py`) define o que pode entrar nessa mochila. Cada agente também tem sua própria mochila menor (`PlannerState`, `ReplanState`, etc.) com só o que ele precisa.

---

## 🧩 Como desenvolver seu agente

Todo o esqueleto já está pronto. Você precisa preencher as funções marcadas com `TODO` dentro de `nodes/SEU_AGENTE/nodes.py`.

### Passo a passo

**1. Abra `nodes/SEU_AGENTE/nodes.py` e preencha as funções**

Cada função recebe os dados do estado, faz alguma coisa, e devolve o estado atualizado:

```python
def gerar_cronograma_node(state: PlannerState) -> PlannerState:
    # TODO: criar o cronograma com base nas preferências do usuário

    cronograma = ...  # sua lógica aqui

    return {**state, "current_plan": cronograma}
    #        ↑ sempre mantenha os dados anteriores com **state
```

> ⚠️ **Importante:** sempre retorne `{**state, "campo": valor}`. Nunca retorne `None` ou um dicionário vazio — isso quebra o fluxo.

---

**2. Para salvar ou buscar dados no banco**

```python
from assistente_estudos.db.database import SessionLocal
from assistente_estudos.db.models import SessaoEstudo

def persistir_cronograma_node(state: PlannerState) -> PlannerState:
    db = SessionLocal()   # abre conexão com o banco
    try:
        registro = SessaoEstudo(usuario_id=state["usuario_id"], ...)
        db.add(registro)
        db.commit()
        return {**state, "plano_id": registro.id}
    finally:
        db.close()        # sempre feche — libera a conexão
```

---

**3. Para usar a IA (LLM) dentro de um passo**

```python
import os
from langchain_ollama import ChatOllama
from assistente_estudos.nodes.SEU_AGENTE.tools import TOOLS

llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "llama3:8b"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
)
resposta = llm.bind_tools(TOOLS).invoke(mensagens)
```

---

**4. Para criar uma "tool" (função que a IA pode chamar)**

Abra `nodes/SEU_AGENTE/tools.py`:

```python
from langchain_core.tools import tool

@tool
def calcular_horas_disponiveis(dias_por_semana: int, horas_por_dia: float) -> float:
    """Calcula o total de horas disponíveis por semana.
    A IA usa a descrição acima para saber quando chamar esta função.
    """
    return dias_por_semana * horas_por_dia

TOOLS = [calcular_horas_disponiveis]
```

---

### O que você precisa mexer × o que não precisa

| Você mexe | Não precisa mexer |
|---|---|
| `nodes/SEU_AGENTE/nodes.py` — lógica dos passos | `nodes/SEU_AGENTE_node.py` — a porta de entrada já está conectada |
| `nodes/SEU_AGENTE/tools.py` — funções para a IA | `nodes/SEU_AGENTE/graph.py` — a ordem dos passos já está definida |
| `nodes/SEU_AGENTE/state.py` — se precisar de novos campos | `api/routes.py` — a rota HTTP já existe |
| | `db/models.py` — as tabelas já estão criadas |

---

### Passos de cada agente

| Agente | Passos internos |
|---|---|
| **planner** | coletar preferências → gerar cronograma → validar → salvar |
| **replan** | analisar desvio → recalcular cronograma → salvar |
| **simulation** | preparar simulado → executar → avaliar resultado → salvar |
| **analysis** ✅ | coletar dados → calcular scores → calcular prontidão → identificar fragilidades → gerar parecer → salvar |
| **report** | coletar dados → gerar relatório → exportar → salvar |

---

## 🌐 Rotas disponíveis na API

Após subir o servidor, acesse **`http://localhost:8000/docs`** para ver e testar todas as rotas de forma visual.

| Método | Rota | O que faz |
|---|---|---|
| `GET` | `/api/health` | Verifica se o servidor está no ar |
| `POST` | `/api/usuarios` | Cadastra um novo usuário |
| `GET` | `/api/usuarios/{id}` | Busca um usuário pelo ID |
| `POST` | `/api/sessoes` | Registra uma sessão de estudo |
| `POST` | `/api/simulados` | Registra o resultado de um simulado |
| `POST` | `/api/analise/{id}` | Roda a análise de desempenho completa |
| `GET` | `/api/analise/{id}/historico` | Histórico de análises do usuário |
| `GET` | `/api/analise/{id}/ultimo` | Análise mais recente do usuário |
| `POST` | `/api/agentes/planner` | Roda o agente de planejamento |
| `POST` | `/api/agentes/replan` | Roda o agente de replanejamento |
| `POST` | `/api/agentes/simulation` | Roda o agente de simulação |
| `POST` | `/api/agentes/analysis` | Roda o agente de análise |
| `POST` | `/api/agentes/report` | Roda o agente de relatório |
| `POST` | `/api/agentes/pipeline` | Roda todos os agentes em sequência |

**Exemplo de chamada:**

```bash
curl -X POST http://localhost:8000/api/agentes/planner \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid-do-usuario",
    "study_goal": "Passar no ENEM",
    "subjects": ["Matemática", "Português"],
    "available_time_hours": 2.0,
    "study_days_per_week": 5
  }'
```

---

## 🗄 Banco de dados

### Por que não escrevemos SQL direto

Usamos o **SQLAlchemy**, uma biblioteca que deixa você trabalhar com o banco usando Python puro. Isso tem duas vantagens principais:

- **Mais fácil de ler e escrever** — você usa objetos Python, não strings de SQL
- **Mais seguro** — elimina uma categoria inteira de bugs e falhas de segurança

Em vez de:
```sql
INSERT INTO usuarios (nome, email) VALUES ('Ana', 'ana@exemplo.com');
```

Você escreve:
```python
usuario = Usuario(nome="Ana", email="ana@exemplo.com")
db.add(usuario)
db.commit()
```

### Tabelas do banco

<details>
<summary><strong>usuarios</strong> — quem usa o sistema</summary>

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | String | Identificador único (UUID gerado automaticamente) |
| `nome` | String | Nome completo |
| `email` | String | E-mail (único — não pode repetir) |
| `criado_em` | DateTime | Quando o cadastro foi feito |

</details>

<details>
<summary><strong>sessoes_estudo</strong> — cada vez que o usuário estuda</summary>

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | String | Identificador único |
| `usuario_id` | String | A qual usuário pertence |
| `disciplina` | String | Ex: "Matemática" |
| `topico` | String | Ex: "Funções do 2º grau" |
| `data` | DateTime | Quando aconteceu |
| `duracao_minutos` | Integer | Quanto tempo durou |
| `concluido` | Boolean | Se terminou ou parou no meio |
| `dificuldade_percebida` | Integer | Como o usuário achou: 1 (fácil) a 5 (difícil) |

</details>

<details>
<summary><strong>resultados_simulados</strong> — resultado de cada simulado</summary>

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | String | Identificador único |
| `usuario_id` | String | A qual usuário pertence |
| `disciplina` | String | Disciplina do simulado |
| `topico` | String | Tópico avaliado |
| `data` | DateTime | Quando foi feito |
| `total_questoes` | Integer | Quantas questões tinha |
| `acertos` | Integer | Quantas acertou |
| `taxa_acerto` | Float | Proporção de acertos (ex: 0.7 = 70%) |
| `nivel_dificuldade` | String | `basico`, `intermediario` ou `avancado` |

</details>

<details>
<summary><strong>scores_prontidao</strong> — resultado de cada análise de desempenho</summary>

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | String | Identificador único |
| `usuario_id` | String | A qual usuário pertence |
| `score_dominio` | Float | % de acerto médio nos simulados |
| `score_consistencia` | Float | % de sessões de estudo concluídas |
| `score_retencao` | Float | Se o desempenho melhorou ao longo do tempo |
| `indice_prontidao` | Float | Nota final de 0 a 100 |
| `classificacao` | String | `risco_alto`, `moderado` ou `alta_probabilidade` |
| `topicos_frageis` | Text | Lista dos tópicos com pior desempenho |
| `tendencia` | String | `melhorando`, `estavel` ou `piorando` |
| `parecer_llm` | Text | Texto explicativo gerado pela IA |
| `criado_em` | DateTime | Quando a análise foi feita |

</details>

---

## 🐳 Subindo com Docker

Docker garante que **todos da equipe rodam o sistema no mesmo ambiente**, sem precisar instalar PostgreSQL, Ollama ou configurar nada manualmente.

### O que sobe junto

| Serviço | Porta | O que é |
|---|---|---|
| `postgres` | 5432 | Banco de dados |
| `pgadmin` | 5050 | Tela visual para ver o banco no navegador |
| `ollama` | 11434 | A IA rodando localmente |
| `backend` | 8000 | O servidor deste projeto |

> Os dados do banco e os modelos de IA ficam salvos em volumes — não somem quando você desliga o Docker.

### Como subir

**1. Copie o arquivo de configuração:**
```bash
cp .env.example .env
```
Não precisa alterar nada para rodar localmente — os valores já estão corretos para Docker.

**2. Suba tudo:**
```bash
docker compose up --build
```

**3. Baixe o modelo de IA (só precisa fazer isso uma vez):**
```bash
docker compose exec ollama ollama pull llama3:8b
```

**4. Pronto! Acesse:**

| O que | Endereço | Login |
|---|---|---|
| API | `http://localhost:8000` | — |
| Documentação visual da API | `http://localhost:8000/docs` | — |
| Banco de dados (visual) | `http://localhost:5050` | `admin@estudos.com` / `admin123` |

### Outros comandos

```bash
# Desligar os serviços
docker compose down

# Desligar e apagar todos os dados (banco + modelos de IA)
docker compose down -v

# Ver o que está acontecendo no servidor em tempo real
docker compose logs -f backend
```

---

## 💻 Rodando sem Docker

Só use isso se tiver PostgreSQL e Ollama instalados na máquina. Caso contrário, use o Docker acima.

```bash
# 1. Criar ambiente virtual Python
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .\.venv\Scripts\Activate.ps1   # Windows

# 2. Instalar as bibliotecas
pip install -r requirements.txt

# 3. Criar o banco no PostgreSQL (rode no psql ou pgAdmin)
# CREATE DATABASE assistente_estudos;
# CREATE USER estudos WITH PASSWORD 'estudos123';
# GRANT ALL PRIVILEGES ON DATABASE assistente_estudos TO estudos;

# 4. Copiar e ajustar as configurações
cp .env.example .env
# No .env, troque "postgres" por "localhost" na DATABASE_URL
# e "ollama" por "localhost" na OLLAMA_BASE_URL

# 5. Ligar o servidor
uvicorn main:app --reload
```

As tabelas são criadas automaticamente quando o servidor liga pela primeira vez.

---

## 📦 Dependências

| Pacote | Para que serve |
|---|---|
| `langgraph` | Controla a ordem de execução dos agentes |
| `langchain` | Ferramentas base para trabalhar com IA |
| `langchain-ollama` | Conecta o código ao Ollama |
| `ollama` | Biblioteca Python para o Ollama |
| `fastapi` | Cria o servidor e as rotas HTTP |
| `uvicorn` | Roda o servidor FastAPI |
| `sqlalchemy` | Acesso ao banco de dados sem SQL manual |
| `psycopg2-binary` | Conector entre o SQLAlchemy e o PostgreSQL |
| `pydantic` | Valida os dados que chegam e saem da API |
| `python-dotenv` | Lê o arquivo `.env` com as configurações |
| `jinja2` | Templates HTML (reservado para uso futuro) |
