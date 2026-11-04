# 🔬 Deep Agents Research Assistant

Sistema de inteligência artificial autônomo para pesquisa, triagem, avaliação metodológica e síntese crítica de artigos científicos, construído com o framework **Deep Agents (LangChain)**, **FastAPI** e **arXiv**.

A arquitetura do backend segue a organização modular de microsserviço estabelecida no `agent-chat-sse-fastapi-01`, com suporte a execução CLI interativa e servidor de API HTTP com streaming SSE.

---

## 🏗️ Arquitetura e Componentes

```
┌────────────────────────────────────────────────────────────────────────┐
│               Research Assistant (Deep Agent Supervisor)               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    ▼                               ▼                               ▼
┌───────────────────────┐ ┌───────────────────┐ ┌───────────────────────┐
│  Tool: ArXiv Search   │ │  Skill Científica │ │ Subagente Metodologia │
│ (search_arxiv_articles)│ │ (Análise Crítica) │ │(methodology-reviewer) │
└───────────────────────┘ └───────────────────┘ └───────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Filesystem Workspace do Agente                       │
│  - Memória Persistente: agent_workspace/memories/AGENTS.md             │
│  - Relatórios Gerados: agent_workspace/reports/relatorio_*.md          │
│  - Segurança: Human-in-the-Loop (HITL) em operações de escrita         │
└────────────────────────────────────────────────────────────────────────┘
```

1. **LLM & Raciocínio:** Integrado ao Google GenAI (`gemini-2.5-flash-lite`) via `langchain-google-genai`.
2. **Ferramenta de Pesquisa (Tool):** Busca direta no repositório oficial do arXiv (`tools.py`) sem necessidade de chaves de API externas.
3. **Skill Especializada:** Roteiro metódico de análise acadêmica (`skills/scientific-article-analysis/SKILL.md`) carregado sob demanda pelo agente via progressive disclosure.
4. **Subagente Especialista:** Delegação de tarefas intensivas de auditoria metodológica e detecção de vieses para o subagente `methodology-reviewer` (Context Quarantine).
5. **Memória Persistente & Workspace:** Diretrizes de estilo em `agent_workspace/memories/AGENTS.md` e saída de relatórios estruturados em Markdown em `agent_workspace/reports/`.
6. **Human-in-the-Loop (HITL):** Interrupção controlada antes de gravar arquivos em disco, solicitando aprovação humana.

---

## 📁 Estrutura do Projeto

```
.
├── app/
│   ├── core/
│   │   ├── config.py         # Configurações Pydantic BaseSettings lendo .env
│   │   ├── llm.py            # Fábrica get_llm() para Google GenAI (Gemini)
│   │   ├── logger.py         # Logger estruturado com RichHandler
│   │   └── __init__.py
│   ├── agents.py             # Agente Deep Agent, prompts, subagente e init_agent()
│   ├── tools.py              # Ferramenta search_arxiv_articles integrada ao arXiv
│   ├── schemas.py            # Schemas Pydantic de requisição e resposta
│   ├── routes.py             # Rotas FastAPI (/health, /research, /chat/stream SSE)
│   ├── main.py               # FastAPI com lifespan + CLI interativo
│   └── __init__.py
│
├── agent_workspace/          # Sandbox operacional do agente
│   ├── memories/
│   │   └── AGENTS.md         # Memória e preferências persistentes
│   └── reports/              # Relatórios acadêmicos gerados
│
├── skills/
│   └── scientific-article-analysis/
│       └── SKILL.md          # Especificação de Agent Skill acadêmica
│
├── pyproject.toml            # Dependências gerenciadas via uv
├── uv.lock
├── .env                      # Chaves e variáveis locais
├── .env.example
├── .gitignore
└── main.py                   # Ponto de entrada raiz
```

---

## 🚀 Instalação e Configuração

### 1. Pré-requisito
Certifique-se de ter o [uv](https://docs.astral.sh/uv/) instalado:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Configurar Variáveis de Ambiente
Copie o arquivo de exemplo e insira sua chave da API Google Gemini:
```bash
cp .env.example .env
```

Edite o arquivo `.env`:
```env
GEMINI_API_KEY="sua_chave_gemini_aqui"
GEMINI_MODEL="gemini-2.5-flash-lite"
GOOGLE_API_KEY="sua_chave_gemini_aqui"

HOST="0.0.0.0"
PORT=8000
DEBUG=true
```

### 3. Sincronizar Dependências
```bash
uv sync
```

---

## 💬 Como Conversar com o Agente

Existem três formas principais de interagir com o Research Assistant:

### Modo 1: Chat Interativo no Terminal (Mais Rápido)
Inicie uma sessão de chat contínua no terminal com memória de contexto:
```bash
uv run python main.py
```
*(ou explicitamente com `uv run python main.py --chat`)*

> Digite suas dúvidas, peça comparações de artigos ou solicite pesquisas. Para encerrar, digite `sair` ou pressione `Ctrl + C`.

---

### Modo 2: Pesquisa Direta via Terminal (Modo Único / One-shot)
Executa a pesquisa no arXiv, audita a metodologia com o subagente e salva o relatório em `agent_workspace/reports/`:
```bash
uv run python main.py -q "Mecanismos de Atenção em Transformers"
```

Com aprovação humana antes de gravar o relatório (**Human-in-the-Loop**):
```bash
uv run python main.py -q "Mecanismos de Atenção em Transformers" --hitl
```

---

### Modo 3: Servidor de API FastAPI (HTTP & SSE Streaming)
Inicia o servidor de API web compatível com frontends reativos:
```bash
uv run python main.py --serve
```
*(ou via uvicorn diretamente: `uv run uvicorn app.main:app --reload --port 8000`)*

Após iniciar:
- **Documentação Interativa (Swagger UI):** Acesse `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`

#### Exemplo de requisição via cURL (`POST /research`):
```bash
curl -X POST "http://localhost:8000/research" \
     -H "Content-Type: application/json" \
     -d '{"query": "Quantum Computing Error Correction"}'
```

#### Exemplo de streaming SSE (`POST /chat/stream`):
```bash
curl -N -X POST "http://localhost:8000/chat/stream" \
     -H "Content-Type: application/json" \
     -d '{"thread_id": "minha-thread-123", "text": "Quais são as novidades em RLHF?"}'
```

---

## 🧪 Verificação de Integridade

Para validar se o agente, o LLM e as ferramentas estão compilando corretamente sem efetuar chamadas externas:
```bash
uv run python main.py --check-only
```
