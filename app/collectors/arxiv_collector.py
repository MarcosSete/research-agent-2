import httpx
import feedparser
from datetime import datetime
from app.collectors.base import BaseCollector
from app.models.paper import Paper, Author, SourceName, Source, SearchResult


ARXIV_API_URL = "https://export.arxiv.org/api/query"


class ArxivCollector(BaseCollector):
    def search(self, query: str, max_results: int = 20) -> SearchResult:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        response = httpx.get(
            ARXIV_API_URL,
            params=params,
            timeout=30.0,
            follow_redirects=True,
        )
        response.raise_for_status()

        feed = feedparser.parse(response.text)
        papers = [
            paper
            for entry in feed.entries
            if (paper := self._parse_entry(entry)) is not None
        ]

        return SearchResult(
            query=query,
            source=SourceName.ARXIV,
            papers=papers,
            total_found=len(papers),
        )

    def _parse_entry(self, entry) -> Paper | None:
        title = entry.get("title")
        abstract = entry.get("summary")
        authors_data = entry.get("authors") or []
        entry_id = entry.get("id")

        if not title or not abstract or not authors_data or not entry_id:
            return None

        authors = [
            Author(name=author["name"])
            for author in authors_data
            if author.get("name")
        ]
        if not authors:
            return None

        pdf_url = None
        for link in entry.get("links", []):
            if link.get("title") == "pdf" and link.get("href"):
                pdf_url = link["href"]
                break

        published = None
        published_raw = entry.get("published")
        if published_raw:
            try:
                published = datetime.strptime(
                    published_raw,
                    "%Y-%m-%dT%H:%M:%SZ",
                ).date()
            except ValueError:
                pass

        return Paper(
            title=title.replace("\n", " ").strip(),
            abstract=abstract.replace("\n", " ").strip(),
            authors=authors,
            source=Source(
                name=SourceName.ARXIV,
                url=entry_id,
            ),
            published_date=published,
            pdf_url=pdf_url,
        )
