from pathlib import Path
import yaml
from pydantic import BaseModel, Field

# Sobe 2 níveis a partir deste arquivo (app/config/profile.py -> app/config -> app -> raiz do projeto)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROFILE_PATH = PROJECT_ROOT / "config" / "research_profile.yaml"

class ResearchProfile(BaseModel):
    interests: list[str]
    priority: dict[str,int] = Field(default_factory=dict)
    ignored: list[str] = Field(default_factory=list)
    favorite_authors: list[str] = Field(default_factory=list)
    favorite_conferences: list[str] = Field(default_factory=list)
    reading_level: str = "intermediate"
    max_daily_papers: int = 20
    summary_style: str = "technical"



def load_research_profile( path: str | Path = DEFAULT_PROFILE_PATH) -> ResearchProfile:
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return ResearchProfile(**raw)