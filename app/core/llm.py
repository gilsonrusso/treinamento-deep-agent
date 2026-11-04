from app.core.config import settings
from app.core.logger import logger


def get_llm():
    """
    Retorna a instância configurada do LLM.
    Suporta Google GenAI (Gemini), OpenAI e Anthropic com base no settings.
    """
    google_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
    if google_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            model = settings.GEMINI_MODEL or "gemini-2.5-flash-lite"
            logger.info(f"Inicializando LLM Google GenAI: [bold green]{model}[/bold green]")
            return ChatGoogleGenerativeAI(
                model=model,
                google_api_key=google_key,
                temperature=0.0,
                max_retries=3,
                streaming=True,
            )
        except ImportError as exc:
            logger.error("Pacote langchain_google_genai não encontrado.")
            raise exc

    if settings.OPENAI_API_KEY:
        try:
            from langchain_openai import ChatOpenAI

            model = settings.MODEL_NAME or "gpt-4o-mini"
            logger.info(f"Inicializando LLM OpenAI: [bold green]{model}[/bold green]")
            return ChatOpenAI(
                model=model,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.0,
                streaming=True,
            )
        except ImportError as exc:
            logger.error("Pacote langchain_openai não encontrado.")
            raise exc

    if settings.ANTHROPIC_API_KEY:
        try:
            from langchain_anthropic import ChatAnthropic

            model = settings.MODEL_NAME or "claude-3-5-sonnet-latest"
            logger.info(f"Inicializando LLM Anthropic: [bold green]{model}[/bold green]")
            return ChatAnthropic(
                model=model,
                api_key=settings.ANTHROPIC_API_KEY,
                temperature=0.0,
                streaming=True,
            )
        except ImportError as exc:
            logger.error("Pacote langchain_anthropic não encontrado.")
            raise exc

    logger.warning("Nenhuma chave de API (GEMINI_API_KEY, GOOGLE_API_KEY ou OPENAI_API_KEY) encontrada no settings.")
    return None
