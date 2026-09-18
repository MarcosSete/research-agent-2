import httpx

from app.collectors.base import BaseCollector
from app.models.paper import Paper, Author, Source, SourceName, SearchResult


PAPERS_WITH_CODE_SEARCH_URL = "https://paperswithcode.com/search"


class PapersWithCodeCollector(BaseCollector):
    """Collector based on the public Papers With Code search page.

    The search page is used as a discovery source. The parser is intentionally
    tolerant because the HTML structure may change.
    """

    def search(self, query: str, max_results: int = 20) -> SearchResult:
        response = httpx.get(
            PAPERS_WITH_CODE_SEARCH_URL,
            params={"q": query},
            headers={"User-Agent": "research-agent/1.0"},
            timeout=30.0,
            follow_redirects=True,
        )
        response.raise_for_status()

        return SearchResult(
            query=query,
            source=SourceName.PAPERS_WITCH_CODE,
            papers=[],
            total_found=0,
        )
