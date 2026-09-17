# app/collectors/semantic_scholar_collector.py
import httpx
from datetime import date
from app.collectors.base import BaseCollector
from app.models.paper import Paper, Author, Source, SourceName, SearchResult

SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


class SemanticScholarCollector(BaseCollector):
    def search(self, query: str, max_results: int = 20) -> SearchResult:
        params = {
            "query": query,
            "limit": max_results,
            "fields": "title,abstract,authors,venue,externalIds,citationCount,openAccessPdf,publicationDate",
        }
        response = httpx.get(SEMANTIC_SCHOLAR_API_URL, params=params, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
        data = response.json()

        papers = [p for item in data.get("data", []) if (p := self._parse_item(item)) is not None]

        return SearchResult(
            query=query,
            source=SourceName.SEMANTIC_SCHOLAR,
            papers=papers,
            total_found=len(papers),
        )

    def _parse_item(self, item: dict) -> Paper | None:
        # Semantic Scholar às vezes retorna entradas sem abstract ou sem autores - descartamos
        if not item.get("abstract") or not item.get("authors"):
            return None

        authors = [Author(name=a["name"]) for a in item["authors"] if a.get("name")]
        if not authors:
            return None

        published = None
        if item.get("publicationDate"):
            try:
                published = date.fromisoformat(item["publicationDate"])
            except ValueError:
                pass

        pdf_info = item.get("openAccessPdf") or {}

        return Paper(
            title=item["title"],
            abstract=item["abstract"],
            authors=authors,
            source=Source(
                name=SourceName.SEMANTIC_SCHOLAR,
                url=f"https://www.semanticscholar.org/paper/{item['paperId']}",
            ),
            published_date=published,
            conference=item.get("venue") or None,
            pdf_url=pdf_info.get("url"),
            citations=item.get("citationCount") or 0,
        )