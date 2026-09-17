import httpx

from app.collectors.base import BaseCollector
from app.models.paper import Paper, Author, Source, SourceName, SearchResult


HUGGINGFACE_PAPERS_SEARCH_URL = "https://huggingface.co/api/papers/search"


class HuggingFaceCollector(BaseCollector):
    def search(self, query: str, max_results: int = 20) -> SearchResult:
        params = {
            "q": query,
            "limit": max_results,
        }

        response = httpx.get(
            HUGGINGFACE_PAPERS_SEARCH_URL,
            params=params,
            timeout=30.0,
            follow_redirects=True,
        )
        response.raise_for_status()

        data = response.json()
        items = data if isinstance(data, list) else data.get("papers", data.get("results", []))

        papers = [
            paper
            for item in items
            if (paper := self._parse_item(item)) is not None
        ]

        return SearchResult(
            query=query,
            source=SourceName.HUGGINGFACE,
            papers=papers,
            total_found=len(papers),
        )

    def _parse_item(self, item: dict) -> Paper | None:
        paper = item.get("paper") if isinstance(item.get("paper"), dict) else item

        paper_id = paper.get("id") or paper.get("paperId") or item.get("id")
        title = paper.get("title")
        summary = paper.get("summary") or paper.get("abstract")
        authors_data = paper.get("authors") or []

        if not paper_id or not title or not summary or not authors_data:
            return None

        authors = []
        for author in authors_data:
            if isinstance(author, str):
                name = author
            else:
                name = author.get("name")
            if name:
                authors.append(Author(name=name))

        if not authors:
            return None

        published = None
        published_raw = paper.get("publishedAt") or paper.get("published_at")
        if published_raw:
            try:
                published = published_raw[:10]
                from datetime import date
                published = date.fromisoformat(published)
            except (ValueError, TypeError):
                published = None

        arxiv_url = f"https://arxiv.org/abs/{paper_id}"

        return Paper(
            title=title,
            abstract=summary,
            authors=authors,
            source=Source(
                name=SourceName.HUGGINGFACE,
                url=f"https://huggingface.co/papers/{paper_id}",
            ),
            published_date=published,
            pdf_url=arxiv_url.replace("/abs/", "/pdf/"),
            has_code=bool(paper.get("githubRepo") or paper.get("github_repo")),
        )
