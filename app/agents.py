from typing import Any, Optional
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings
from app.core.llm import get_llm
from app.core.logger import logger
from app.tools import search_arxiv_articles

# Instância única do agente inicializada no lifespan ou na inicialização
_agent = None

RESEARCH_SUPERVISOR_PROMPT = """Você é o Research Assistant, um agente de IA de nível avançado especializado em investigação e análise científica rigorosa.

Seu objetivo é auxiliar pesquisadores na busca, triagem, avaliação metodológica e síntese crítica de artigos científicos.

## Diretrizes de Execução:
1. **Pesquisa Acadêmica:** Utilize a ferramenta `search_arxiv_articles` para localizar preprints e publicações relevantes sobre o tema solicitado no repositório arXiv.
2. **Aplicação de Skills:** Para conduzir a análise crítica dos artigos, ative e siga estritamente as etapas da skill `scientific-article-analysis` (objetivos, metodologia, resultados, limitações e contribuições).
3. **Delegação a Subagentes:** Para auditorias aprofundadas de desenho experimental, análise estatística e detecção de vieses, delegue a tarefa ao subagente `methodology-reviewer`.
4. **Memória e Preferências:** Respeite rigorosamente as preferências descritas no arquivo de memória persistente `/agent_workspace/memories/AGENTS.md`.
5. **Geração de Relatórios:** Salve a síntese final detalhada em formato Markdown no diretório `agent_workspace/reports/` (ex.: `agent_workspace/reports/relatorio_<tema>.md`).

Mantenha sempre postura ética, precisão conceitual e declare explicitamente quando houver limitações nos resumos encontrados.
"""

METHODOLOGY_SUBAGENT = {
    "name": "methodology-reviewer",
    "description": (
        "Especialista em auditoria metodológica e avaliação crítica de desenhos "
        "experimentais, técnicas estatísticas, tamanho amostral, vieses e limitações em artigos científicos."
    ),
    "system_prompt": (
        "Você é um revisor acadêmico sênior focado exclusivamente em rigor metodológico. "
        "Ao examinar dados de artigos, avalie criticamente: "
        "1. Adequação da metodologia ao problema proposto. "
        "2. Validade interna e externa (amostragem, controles, variáveis de confusão). "
        "3. Coerência entre evidências apresentadas e conclusões. "
        "4. Limitações não declaradas e ameaças à validade científica. "
        "Retorne um parecer técnico, direto e estruturado para o agente coordenador."
    ),
}


def init_agent(
    checkpointer: Any = None,
    enable_hitl: bool = False,
    model_override: Optional[Any] = None,
) -> Any:
    """
    Inicializa e compila a instância do Deep Agent.
    Pode ser chamado no startup do FastAPI (lifespan) ou no CLI.
    """
    global _agent

    logger.info("Inicializando Research Deep Agent...")

    # Garante que os diretórios necessários existem
    settings.WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    (settings.WORKSPACE_DIR / "memories").mkdir(parents=True, exist_ok=True)
    (settings.WORKSPACE_DIR / "reports").mkdir(parents=True, exist_ok=True)

    # Checkpointer de memória para checkpoints e suporte a HITL
    if checkpointer is None:
        checkpointer = MemorySaver()

    # Backend com acesso virtualizado à raiz do projeto
    backend = FilesystemBackend(
        root_dir=settings.BASE_DIR,
        virtual_mode=True,
    )

    # Interrupção de escrita (Human-in-the-Loop)
    interrupt_on = {"write_file": True} if enable_hitl else None

    # Modelo: usa LLM instanciado ou o modelo do settings
    model = model_override or get_llm() or settings.model_identifier

    _agent = create_deep_agent(
        model=model,
        tools=[search_arxiv_articles],
        system_prompt=RESEARCH_SUPERVISOR_PROMPT,
        subagents=[METHODOLOGY_SUBAGENT],
        skills=["/skills/"],
        memory=[settings.MEMORY_FILE],
        backend=backend,
        checkpointer=checkpointer,
        interrupt_on=interrupt_on,
        name="research-supervisor",
    )

    logger.info("Research Deep Agent [bold green]compilado com sucesso![/bold green]")
    return _agent


def get_agent():
    """Retorna a instância compilada do agente."""
    global _agent
    if _agent is None:
        # Inicialização sob demanda com configurações padrão
        _agent = init_agent()
    return _agent
