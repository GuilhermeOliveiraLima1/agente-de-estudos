# Setup de Infraestrutura

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando
- Mínimo de **4 GB de RAM** alocados para o Docker

### Configurar memória do Docker Desktop

Docker Desktop → **Settings → Resources → Memory** → definir pelo menos `4096 MB` → **Apply & Restart**

> Sem isso, o modelo de LLM não consegue carregar e a API retorna erro 500.

---

## 1. Configurar variáveis de ambiente

Copie o arquivo de exemplo e ajuste se necessário:

```bash
cp .env.example .env
```

Conteúdo padrão do `.env`:

```env
DATABASE_URL=postgresql://estudos:estudos123@postgres:5432/assistente_estudos
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2:1b
```

---

## 2. Subir os containers

```bash
docker compose up -d
```

Isso sobe quatro serviços:

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| `backend` | 8000 | API FastAPI |
| `postgres` | 5432 | Banco de dados |
| `ollama` | 11434 | Servidor de LLM |
| `pgadmin` | 5050 | Interface visual do banco |

Aguarde o postgres ficar `healthy` antes de continuar:

```bash
docker compose ps
```

---

## 3. Baixar o modelo de LLM

**Este passo é obrigatório e precisa ser feito uma vez após a primeira subida dos containers.**

O container do Ollama sobe vazio — o modelo precisa ser baixado manualmente:

```bash
docker exec agente-de-estudos-ollama-1 ollama pull llama3.2:1b
```

O modelo fica salvo no volume `ollama_data`. Nas próximas subidas dos containers ele já estará disponível — não precisa baixar novamente.

Confirme que o modelo foi baixado:

```bash
docker exec agente-de-estudos-ollama-1 ollama list
```

---

## 4. Verificar que tudo está funcionando

```bash
curl http://localhost:8000/api/health
# esperado: {"status":"ok","service":"assistente-estudos-api"}
```

---

## Recriando o backend após mudar o `.env`

O `docker restart` simples **não relê** o `env_file` do Compose. Para aplicar mudanças no `.env`:

```bash
docker compose up -d backend
```

---

## Acessos úteis

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| API | http://localhost:8000 | — |
| Documentação da API | http://localhost:8000/docs | — |
| pgAdmin | http://localhost:5050 | admin@estudos.com / admin123 |
| Banco (conexão direta) | localhost:5432 | estudos / estudos123 |
