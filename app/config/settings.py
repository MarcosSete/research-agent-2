from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_env_file() -> Path:
    """
    Search for the .env file from this file's directory up to the project root.

    This makes environment loading independent of the working directory
    (PyCharm, terminal, Docker, CI, pytest, etc.).
    """
    here = Path(__file__).resolve()

    for directory in [here.parent, *here.parents]:
        candidate = directory / ".env"
        if candidate.exists():
            return candidate

    return Path(".env")


ENV_FILE = find_env_file()


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql://research:research@localhost:5432/research_agent"
    )
    qdrant_url: str = Field(default="http://localhost:6333")
    max_daily_papers: int = Field(default=20)
    relevance_threshold: float = Field(default=0.6)

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
