from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_env_file() -> Path:
    """
    Procura o arquivo .env subindo a árvore de diretórios a partir
    deste arquivo (app/config/settings.py) até a raiz do projeto.

    Isso torna o carregamento independente do working directory
    (PyCharm, terminal, Docker, CI, pytest etc.).
    """
    here = Path(__file__).resolve()

    # Começa na pasta do arquivo e sobe até a raiz do disco
    for directory in [here.parent, *here.parents]:
        candidate = directory / ".env"
        if candidate.exists():
            return candidate

    # Fallback: cwd (mantém o comportamento padrão)
    return Path(".env")


ENV_FILE = find_env_file()


class Settings(BaseSettings):

    # Banco relacional
    database_url: str = Field(
        default="postgresql://research:research123@localhost:5432/research_agent"
    )

    # Banco vetorial
    qdrant_url: str = Field(
        default="http://localhost:6333"
    )

    # Parâmetros de negócio
    max_daily_papers: int = Field(default=20)
    relevance_threshold: float = Field(default=0.6)

    # DeepSeek
    deepseek_api_key: str = Field(default="")
    deepseek_base_url: str = Field(default="https://api.deepseek.com")
    deepseek_model_fast: str = Field(default="deepseek-chat")
    deepseek_model_smart: str = Field(default="deepseek-reasoner")

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()