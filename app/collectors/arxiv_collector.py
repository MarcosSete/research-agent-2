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

        response = httpx.get(ARXIV_API_URL, params=params, timeout = 30.0,follow_redirects=True)
        response.raise_for_status() ## lança erro se a api falhar (status 4xx/5xx)

        feed = feedparser.parse(response.text)
        papers = [self._parse_entry(entry) for entry in feed.entries]

        return SearchResult(
            query=query,
            source=SourceName.ARXIV,
            papers=papers,
            total_found=len(papers),

        )

    def _parse_entry(self, entry) -> Paper:
        authors = [Author(name = a.name) for a in entry.authors]

        pdf_url = None
        for link in entry.links:
            if link.get("title") == "pdf":
                pdf_url = link.href

        published = datetime.strptime(
            entry.published, "%Y-%m-%dT%H:%M:%SZ"
        ).date()

        return Paper(
            title = entry.title.replace("\n", " ").strip(),
            abstract= entry.summary.replace("\n", " ").strip(),
            authors = authors,
            source = Source(name=SourceName.ARXIV,url=entry.id ),
            published_date=published,
            pdf_url=pdf_url,

        )