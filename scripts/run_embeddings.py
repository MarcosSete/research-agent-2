from app.database.session import get_session
from app.database.repository import PaperRepository
from app.embeddings.local_service import LocalEmbeddingService
from app.embeddings.qdrant_store import QdrantStore


def main():
    session = get_session()
    repo = PaperRepository(session)

    service = LocalEmbeddingService()
    store = QdrantStore(vector_dimension=service.dimension)

    papers = repo.get_without_embedding()
    print(f"Papers pendentes de embedding: {len(papers)}")

    if not papers:
        print("Nada a fazer.")
        session.close()
        return

    # Gera todos os embeddings de uma vez (batch) - mais eficiente, como vimos no Passo 2
    textos = [f"{p.title}. {p.abstract}" for p in papers]
    vetores = service.embed_batch(textos)

    for paper, vetor in zip(papers, vetores):
        store.upsert_paper(
            paper_id=paper.id,
            vector=vetor,
            payload={
                "title": paper.title,
                "source": paper.source_name,
                "conference": paper.conference,
            },
        )
        repo.mark_embedded(paper.id)
        print(f"  + embedding gerado: {paper.title}")

    print(f"\nTotal de pontos no Qdrant: {store.count()}")
    session.close()


if __name__ == "__main__":
    main()