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

class Source(BaseModel):
    name: SourceName
    url: HttpUrl
    fetched_at: date = Field(default_factory=date.today)

class Paper(BaseModel):
    title: str
    abstract: str
    authors: list[Author] = Field(min_length=1)
    source: Source
    published_date: date | None = None
    conference: str | None = None
    pdf_url: HttpUrl | None = None
    has_code: bool | None = None
    citations: int = 0

    embedding: list[float  ] | None = None
    relevance_score: float | None = None
    summary: str | None = None

class SearchResult(BaseModel):
    query: str
    source: SourceName
    papers: list[Paper] = Field(default_factory=list)
    total_found: int = 0


## o que seria esse BaseModel e porque ele é passado como argumento das classes?
## Porque as classes não tem os métodos sets e gets?
## O que seria a class SourceName(str, Enum) é um enum? Porque o enum é passado como argumento
## O que seria HttpUrl e como eu poderia usa-lo e porque
## O que seria Field e como eu poderia usa-lo e porque e quais são as opções de uso.