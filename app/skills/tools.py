from langchain_core.tools import tool
from app.database.session import get_session
from app.database.repository import PaperRepository
from app.database.models import PaperORM
from app.collectors.arxiv_collector import ArxivCollector
from app.collectors.semantic_scholar_collector import SemanticScholarCollector
from app.embeddings.local_service import LocalEmbeddingService
from app.embeddings.qdrant_store import QdrantStore
from app.ranking.scorer import PaperScorer
from app.config.research_profile_loader import load_research_profile

# Cache simples em memória - evita recarregar o modelo de embeddings a cada tool call
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
    """Busca papers sobre um tema numa fonte ('arxiv' ou 'semantic_scholar') e
    salva no banco, sem duplicar. Retorna um resumo do resultado."""
    collectors = {
        "arxiv": ArxivCollector(),
        "semantic_scholar": SemanticScholarCollector(),
    }
    collector = collectors.get(source)
    if collector is None:
        return f"Fonte desconhecida: '{source}'. Use 'arxiv' ou 'semantic_scholar'."

    session = get_session()
    repo = PaperRepository(session)
    try:
        result = collector.search(query, max_results=max_results)
        saved = sum(1 for paper in result.papers if repo.save(paper) is not None)
    finally:
        session.close()

    return (
        f"{saved} papers novos salvos de {len(result.papers)} encontrados "
        f"sobre '{query}' em {source}."
    )


@tool
def generate_pending_embeddings() -> str:
    """Gera embeddings para todos os papers do banco que ainda não têm um."""
    session = get_session()
    repo = PaperRepository(session)
    service, store = _get_embedding_backend()

    papers = repo.get_without_embedding()
    if not papers:
        session.close()
        return "Nenhum paper pendente de embedding."

    textos = [f"{p.title}. {p.abstract}" for p in papers]
    vetores = service.embed_batch(textos)

    for paper, vetor in zip(papers, vetores):
        store.upsert_paper(
            paper_id=paper.id,
            vector=vetor,
            payload={"title": paper.title, "source": paper.source_name},
        )
        repo.mark_embedded(paper.id)

    session.close()
    return f"{len(papers)} embeddings gerados e salvos no Qdrant."


@tool
def get_top_ranked_papers(limit: int = 10) -> str:
    """Retorna os papers mais relevantes do banco, ranqueados de acordo com
    o perfil de interesses do usuário."""
    session = get_session()
    profile = load_research_profile()
    service, store = _get_embedding_backend()
    scorer = PaperScorer(profile, embedding_service=service)

    interest_vector = scorer.interest_vector
    if interest_vector is None:
        session.close()
        return "Nenhum interesse configurado no perfil de pesquisa."

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
    session.close()

    if not ranked:
        return "Nenhum paper ranqueado encontrado."

    lines = [f"{score:.4f} | {paper.title}" for score, paper in ranked[:limit]]
    return "\n".join(lines)