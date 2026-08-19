
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    #Banco Relacional
    database_url:str = Field(default= "postgresql://research:research123@localhost:5432/research_agent")

    # Banco vetorial
    qdrant_url: str = Field(default = "http://localhost:6333" )

    # Chaves de API
    deepseek_api_key: str = Field(default = "")

    # Pârametros de negócio do sistema.

    max_daily_papers: int = Field(default = 20)
    relevance_threshold: float = Field(default = 0.6)

    model_config = SettingsConfigDict(
    env_file=".env.example",
    env_file_encoding="utf-8",
    extra="ignore",
)

settings = Settings()