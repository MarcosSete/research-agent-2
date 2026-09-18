from langchain_core.tools import tool
import json

from app.database.session import get_session
from app.database.repository import PaperRepository
from app.database.models import PaperORM
from app.collectors.arxiv_collector import ArxivCollector
from app.collectors.semantic_scholar_collector import SemanticScholarCollector
from app.collectors.huggingface_collector import HuggingFaceCollector
from app.embeddings.local_service import LocalEmbeddingService
from app.embeddings.qdrant_store import QdrantStore
from app.ranking.scorer import PaperScorer
from app.config.research_profile_loader import load_research_profile
from app.reports.report_writer import save_research_report

_service = None
_store = None


def _get_embedding_backend():
    global _service, _store
    if _service is None:
        _service = LocalEmbeddingService()
        _store = QdrantStore(vector_dimension=_service.dimension)
    return _service, _store


@tool
def search_and_save_papers(query: str, source: str = "arxiv", max_results: int = 10) -> str:
    """Search a paper source and save results to the database without duplicates."""
    collectors = {
        "arxiv": ArxivCollector(),
        "huggingface": HuggingFaceCollector(),
        "semantic_scholar": SemanticScholarCollector(),
    }
    collector = collectors.get(source)
    if collector is None:
        return (
            f"Unknown source: '{source}'. "
            "Use 'arxiv', 'huggingface', or 'semantic_scholar'."
        )

    session = get_session()
    repo = PaperRepository(session)
    try:
        result = collector.search(query, max_results=max_results)
        saved = sum(1 for paper in result.papers if repo.save(paper) is not None)
    finally:
        session.close()

    return (
        f"{saved} new papers saved out of {len(result.papers)} found "
        f"for '{query}' on {source}."
    )


@tool
def generate_pending_embeddings() -> str:
    """Generate embeddings for all papers that do not have one yet."""
    session = get_session()
    repo = PaperRepository(session)
    service, store = _get_embedding_backend()

    papers = repo.get_without_embedding()
    if not papers:
        session.close()
        return "No papers pending embedding generation."

    texts = [f"{p.title}. {p.abstract}" for p in papers]
    vectors = service.embed_batch(texts)

    for paper, vector in zip(papers, vectors):
        store.upsert_paper(
            paper_id=paper.id,
            vector=vector,
            payload={"title": paper.title, "source": paper.source_name},
        )
        repo.mark_embedded(paper.id)

    session.close()
    return f"{len(papers)} embeddings generated and saved to Qdrant."


@tool
def get_top_ranked_papers(limit: int = 10) -> str:
    """Return the final ranking as JSON while preserving factual metadata for synthesis."""
    session = get_session()
    profile = load_research_profile()
    service, store = _get_embedding_backend()
    scorer = PaperScorer(profile, embedding_service=service)

    interest_vector = scorer.interest_vector
    if interest_vector is None:
        session.close()
        return json.dumps(
            {"error": "No research interests configured in the research profile."},
            ensure_ascii=False,
        )

    similar_results = store.search_similar(interest_vector, limit=50)
    similarity_by_id = {r["id"]: r["score"] for r in similar_results}
    vector_by_id = {
        r["id"]: r.get("vector")
        for r in similar_results
        if r.get("vector") is not None
    }

    papers = (
        session.query(PaperORM)
        .filter(PaperORM.id.in_(similarity_by_id.keys()))
        .all()
    )

    ranked = []
    for paper in papers:
        author_names = [a.name for a in paper.authors]
        score = scorer.score(
            title=paper.title,
            abstract=paper.abstract,
            similarity=similarity_by_id.get(paper.id, 0.0),
            conference=paper.conference,
            author_names=author_names,
            published_date=paper.published_date,
            citations=paper.citations,
            paper_vector=vector_by_id.get(paper.id),
        )
        ranked.append((score, paper))

    ranked.sort(key=lambda x: x[0], reverse=True)

    if not ranked:
        session.close()
        return json.dumps({"papers": []}, ensure_ascii=False)

    selected = ranked[:limit]
    result = {
        "papers": [
            {
                "position": position,
                "title": paper.title,
                "score": round(score, 4),
                "authors": [a.name for a in paper.authors],
                "published": str(paper.published_date) if paper.published_date else None,
                "conference": paper.conference,
                "citations": paper.citations,
                "abstract": paper.abstract,
                "source": str(paper.source_url),
            }
            for position, (score, paper) in enumerate(selected, start=1)
        ]
    }

    session.close()
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool
def save_final_research_report(report: str) -> str:
    """Save the final research synthesis as Markdown and JSON."""
    markdown_path, json_path = save_research_report(report)
    return (
        f"Report saved successfully. "
        f"Markdown: {markdown_path}. JSON: {json_path}."
    )
