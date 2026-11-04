import argparse
import sys
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.agents import get_agent, init_agent
from app.core.config import settings
from app.core.logger import logger
from app.routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[bold blue]Starting up Research Assistant Service (Lifespan)...[/bold blue]")
    init_agent()
    yield
    logger.info("[bold yellow]Shutting down Research Assistant Service...[/bold yellow]")


app = FastAPI(
    title="Research Assistant API (Deep Agents)",
    description="Backend para pesquisa científica e análise com Deep Agents, LangChain, ArXiv e Skills",
    version="1.0.0",
    lifespan=lifespan,
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão das rotas da API
app.include_router(api_router)


def run_interactive_chat(enable_hitl: bool = False):
    """Executa um chat conversacional contínuo com o agente no terminal."""
    agent = init_agent(enable_hitl=enable_hitl)
    thread_id = str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("\n" + "=" * 65)
    print("🤖 RESEARCH ASSISTANT — CHAT INTERATIVO")
    print(f"Sessão iniciada (Thread: {thread_id[:8]}...) | HITL: {'Ativado' if enable_hitl else 'Desativado'}")
    print("Digite sua pergunta ou tema de pesquisa (ou 'sair' para encerrar):")
    print("=" * 65 + "\n")

    while True:
        try:
            user_input = input("\nVocê: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("sair", "exit", "quit", "q"):
                print("\nEncerrando sessão de chat. Até logo!")
                break

            input_payload = {"messages": [{"role": "user", "content": user_input}]}

            for chunk in agent.stream(input_payload, config=config, stream_mode="values"):
                messages = chunk.get("messages", [])
                if messages:
                    last_msg = messages[-1]
                    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                        for tool_call in last_msg.tool_calls:
                            logger.info(f"-> Usando ferramenta: [yellow]{tool_call.get('name')}[/yellow]")

            state = agent.get_state(config)
            if state.values.get("messages"):
                last_ai = state.values["messages"][-1]
                if last_ai.type == "ai" and last_ai.content:
                    print(f"\n[Assistente]:\n{last_ai.content}\n")

            # Tratamento de Human-in-the-Loop caso haja interrupção
            if enable_hitl and state.next:
                print("\n[HUMAN-IN-THE-LOOP] Operação pendente aguardando aprovação:")
                confirm = input("Deseja autorizar a operação de escrita? [S/n]: ").strip().lower()
                if confirm in ("", "s", "sim", "y", "yes"):
                    for chunk in agent.stream(None, config=config, stream_mode="values"):
                        msgs = chunk.get("messages", [])
                        if msgs and hasattr(msgs[-1], "content") and msgs[-1].content:
                            print(f"\n[Assistente]:\n{msgs[-1].content}\n")
                else:
                    print("Operação cancelada.")

        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando sessão de chat. Até logo!")
            break
        except Exception as exc:
            logger.error(f"Erro durante conversa: {exc}")


def run_cli(query: str, enable_hitl: bool = False):
    """Executa o agente para uma única consulta diretamente no terminal."""
    agent = init_agent(enable_hitl=enable_hitl)
    thread_id = str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    logger.info(f"Iniciando pesquisa científica para: [bold cyan]{query}[/bold cyan]")
    logger.info(f"Thread ID: {thread_id} | HITL: {'Ativado' if enable_hitl else 'Desativado'}")

    input_payload = {
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Pesquise e elabore uma análise científica completa sobre: '{query}'. "
                    "Consulte artigos relevantes no arXiv, utilize a skill de análise científica, "
                    "valide a metodologia com o subagente e salve o relatório final em Markdown na pasta agent_workspace/reports/."
                ),
            }
        ]
    }

    try:
        for chunk in agent.stream(input_payload, config=config, stream_mode="values"):
            messages = chunk.get("messages", [])
            if messages:
                last_msg = messages[-1]
                if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    for tool_call in last_msg.tool_calls:
                        logger.info(f"-> Chamada de Ferramenta: [yellow]{tool_call.get('name')}[/yellow]")
                elif hasattr(last_msg, "content") and last_msg.type == "ai":
                    print(f"\n[Resposta do Agente]:\n{last_msg.content}")

        if enable_hitl:
            state = agent.get_state(config)
            if state.next:
                print("\n[HUMAN-IN-THE-LOOP] Operação crítica aguardando aprovação:")
                confirm = input("Deseja aprovar a execução desta operação? [S/n]: ").strip().lower()
                if confirm in ("", "s", "sim", "y", "yes"):
                    for chunk in agent.stream(None, config=config, stream_mode="values"):
                        msgs = chunk.get("messages", [])
                        if msgs and hasattr(msgs[-1], "content"):
                            print(f"\n[Resposta Final]:\n{msgs[-1].content}")

        reports_dir = settings.WORKSPACE_DIR / "reports"
        generated = list(reports_dir.glob("*.md"))
        print("\n" + "=" * 65)
        print(f"Relatórios disponíveis em {reports_dir}:")
        for report in generated:
            print(f"  - {report.name} ({report.stat().st_size} bytes)")

    except Exception as exc:
        logger.error(f"Erro durante execução do agente: {exc}")


def main():
    parser = argparse.ArgumentParser(description="Research Assistant Service (Backend)")
    parser.add_argument("-q", "--query", type=str, help="Executar pesquisa direta (modo comando único)")
    parser.add_argument("-c", "--chat", action="store_true", help="Iniciar chat interativo no terminal")
    parser.add_argument("--hitl", action="store_true", help="Ativar Human-in-the-Loop")
    parser.add_argument("--check-only", action="store_true", help="Validar inicialização do agente")
    parser.add_argument("--serve", action="store_true", help="Iniciar servidor de API FastAPI (Uvicorn)")
    parser.add_argument("--port", type=int, default=settings.PORT, help="Porta do servidor")

    args = parser.parse_args()

    if args.check_only:
        logger.info("Testando integridade do agente...")
        init_agent()
        logger.info("[bold green]Tudo pronto! Agente inicializado com sucesso.[/bold green]")
        return

    if args.serve:
        logger.info(f"Iniciando servidor Uvicorn em {settings.HOST}:{args.port}...")
        uvicorn.run("app.main:app", host=settings.HOST, port=args.port, reload=settings.DEBUG)
        return

    if args.query:
        run_cli(query=args.query, enable_hitl=args.hitl)
        return

    # Por padrão (sem argumentos ou com --chat): Chat Interativo no terminal
    run_interactive_chat(enable_hitl=args.hitl)


if __name__ == "__main__":
    main()
