import json
from collections.abc import AsyncIterable
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langgraph.types import Command

from app.agents import get_agent
from app.core.config import settings
from app.core.logger import logger
from app.schemas import ChatPayload, HealthResponse, ResearchRequest

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Verifica a integridade do serviço e as configurações ativas."""
    agent = get_agent()
    return HealthResponse(
        status="ok",
        model=settings.model_identifier,
        agent_initialized=agent is not None,
        workspace=str(settings.WORKSPACE_DIR),
    )


@router.post("/research")
async def execute_research(payload: ResearchRequest):
    """Executa o ciclo completo de pesquisa no arXiv e geração de relatório."""
    agent = get_agent()
    thread_id = str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    user_prompt = (
        f"Pesquise e elabore uma análise científica completa sobre: '{payload.query}'. "
        "Consulte artigos relevantes no arXiv, utilize a skill de análise científica, "
        "valide a metodologia com o subagente e salve o relatório final em Markdown na pasta agent_workspace/reports/."
    )

    try:
        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": user_prompt}]},
            config=config,
        )

        messages = response.get("messages", [])
        last_message = messages[-1].content if messages else "Sem resposta."

        # Lista relatórios gerados
        reports = [
            f.name for f in (settings.WORKSPACE_DIR / "reports").glob("*.md")
        ]

        return {
            "status": "completed",
            "thread_id": thread_id,
            "response": last_message,
            "reports_available": reports,
        }
    except Exception as exc:
        logger.error(f"Erro na execução da pesquisa: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/chat/stream")
async def stream_chat(payload: ChatPayload):
    """
    Endpoint de streaming SSE (Server-Sent Events) compatível com o padrão do frontend.
    Emite eventos: lifecycle_start, message, tool_start, tool_end, interrupt, lifecycle_end.
    """
    config = {"configurable": {"thread_id": payload.thread_id}}
    agent = get_agent()

    async def event_generator() -> AsyncIterable[str]:
        # Início do ciclo de vida
        yield "event: lifecycle_start\ndata: [START]\n\n"

        if payload.decisions:
            decisions_list = [d.model_dump(exclude_none=True) for d in payload.decisions]
            inputs = Command(resume={"decisions": decisions_list})
        elif payload.text:
            inputs = {"messages": [{"role": "user", "content": payload.text}]}
        else:
            yield "event: error\ndata: Payload inválido: informe 'text' ou 'decisions'\n\n"
            yield "event: lifecycle_end\ndata: [DONE]\n\n"
            return

        try:
            async for event in agent.astream_events(inputs, config=config, version="v2"):
                kind = event.get("event")

                # Tokens de texto gerados pelo modelo
                if kind == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk and hasattr(chunk, "content") and isinstance(chunk.content, str) and chunk.content:
                        # Formata linha a linha para conformidade com a especificação SSE
                        escaped = chunk.content.replace("\n", "\ndata: ")
                        yield f"event: message\ndata: {escaped}\n\n"

                # Início de chamada de ferramenta
                elif kind == "on_tool_start":
                    tool_name = event.get("name", "unknown")
                    yield f"event: tool_start\ndata: {tool_name}\n\n"

                # Conclusão de ferramenta
                elif kind == "on_tool_end":
                    tool_name = event.get("name", "unknown")
                    yield f"event: tool_end\ndata: {tool_name}\n\n"

            # Checagem de interrupção (Human-in-the-Loop)
            state = await agent.aget_state(config)
            if state.tasks and state.tasks[0].interrupts:
                interrupt_val = state.tasks[0].interrupts[0].value
                yield f"event: interrupt\ndata: {json.dumps(interrupt_val)}\n\n"
            else:
                yield "event: lifecycle_end\ndata: [DONE]\n\n"

        except Exception as exc:
            logger.error(f"Erro durante streaming: {exc}")
            yield f"event: error\ndata: {str(exc)}\n\n"
            yield "event: lifecycle_end\ndata: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
