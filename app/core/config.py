from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "./.env", "../.env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API Keys & Provedores
    GEMINI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Modelos
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"
    MODEL_NAME: str = ""

    # Servidor FastAPI
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Observabilidade
    LANGSMITH_TRACING: bool = False
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "deep-agents-training"

    # Diretórios do Agente
    BASE_DIR: Path = BASE_DIR
    WORKSPACE_DIR: Path = BASE_DIR / "agent_workspace"
    SKILLS_DIR: Path = BASE_DIR / "skills"
    MEMORY_FILE: str = "/agent_workspace/memories/AGENTS.md"

    @property
    def api_key(self) -> str:
        """Retorna a chave de API primária configurada (priorizando Gemini/Google)."""
        return self.GEMINI_API_KEY or self.GOOGLE_API_KEY or self.OPENAI_API_KEY or self.ANTHROPIC_API_KEY

    @property
    def model_identifier(self) -> str:
        """Retorna o identificador formatado do modelo para o Deep Agents."""
        if self.MODEL_NAME:
            raw = self.MODEL_NAME.strip().strip('"').strip("'")
            if ":" in raw:
                return raw
            if raw.startswith("gemini"):
                return f"google_genai:{raw}"
            if raw.startswith("gpt-") or raw.startswith("o1") or raw.startswith("o3"):
                return f"openai:{raw}"
            if raw.startswith("claude"):
                return f"anthropic:{raw}"
            return raw

        if self.GEMINI_API_KEY or self.GOOGLE_API_KEY:
            return f"google_genai:{self.GEMINI_MODEL}"
        elif self.OPENAI_API_KEY:
            return "openai:gpt-4o-mini"
        elif self.ANTHROPIC_API_KEY:
            return "anthropic:claude-3-5-sonnet-latest"

        return f"google_genai:{self.GEMINI_MODEL}"


# Instância global de configurações
settings = Settings()
