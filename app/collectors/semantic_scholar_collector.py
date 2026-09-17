# app/collectors/semantic_scholar_collector.py
import time
from datetime import date

import httpx

from app.collectors.base import BaseCollector
from app.models.paper import Paper, Author, Source, SourceName, SearchResult

SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
MAX_RETRIES = 3


class SemanticScholarCollector(BaseCollector):
    def search(self, query: str, max_results: int = 20) -> SearchResult:
        params = {
            "query": query,
            "limit": max_results,
            "fields": "title,abstract,authors,venue,externalIds,citationCount,openAccessPdf,publicationDate",
        }

        for attempt in range(MAX_RETRIES + 1):
            response = httpx.get(
                SEMANTIC_SCHOLAR_API_URL,
                params=params,
                timeout=30.0,
                follow_redirects=True,
            )

            if response.status_code != 429:
                response.raise_for_status()
                break

            if attempt == MAX_RETRIES:
                response.raise_for_status()

            retry_after = response.headers.get("Retry-After")
            try:
                wait_seconds = float(retry_after) if retry_after else 2 ** attempt
            except ValueError:
                wait_seconds = 2 ** attempt

            time.sleep(wait_seconds)

        data = response.json()

        papers = [
            p for item in data.get("data", [])
            if (p := self._parse_item(item)) is not None
        ]

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
