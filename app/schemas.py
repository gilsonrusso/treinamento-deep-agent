from typing import Any, List, Optional
from pydantic import BaseModel, Field


class DecisionItem(BaseModel):
    type: str = Field(description="'approve', 'reject', 'edit' ou 'respond'")
    message: Optional[str] = None
    edited_action: Optional[dict[str, Any]] = None


class ChatPayload(BaseModel):
    thread_id: str = Field(description="Identificador único da conversa")
    text: Optional[str] = Field(default=None, description="Mensagem de pesquisa ou comando do usuário")
    decisions: Optional[List[DecisionItem]] = Field(default=None, description="Decisões para retoma de HITL")


class ResearchRequest(BaseModel):
    query: str = Field(description="Tema de investigação científica a ser pesquisado no arXiv")
    enable_hitl: bool = Field(default=False, description="Habilita Human-in-the-Loop para salvar relatórios")


class HealthResponse(BaseModel):
    status: str
    model: str
    agent_initialized: bool
    workspace: str
