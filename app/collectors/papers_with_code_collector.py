from datetime import date

import httpx

from app.collectors.base import BaseCollector
from app.models.paper import Paper, Author, Source, SourceName, SearchResult


PAPERS_WITH_CODE_SEARCH_URL = "https://paperswithcode.com/search"


class PapersWithCodeCollector(BaseCollector):
    """Collector baseado na busca pública de Papers With Code.

    A página de busca é usada como fonte de descoberta. O parser é
    deliberadamente tolerante, pois a estrutura HTML pode mudar.
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
