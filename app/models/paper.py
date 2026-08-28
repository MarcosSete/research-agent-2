from datetime import date
from enum import Enum
from pydantic import BaseModel,Field, HttpUrl

class SourceName(str, Enum):
    ARXIV: str = "arxiv"
    SEMANTIC_SCHOLAR: str = "semanticscholar"
    HUGGINGFACE: str = "huggingface"
    PAPERS_WITCH_CODE: str = "papers_witche_code"

class Author(BaseModel):
    name: str
    affiliation: str | None = None
