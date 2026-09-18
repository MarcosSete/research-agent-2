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
    print(f"Pending embeddings: {len(papers)}")

    if not papers:
        print("Nothing to do.")
        session.close()
        return

    texts = [f"{p.title}. {p.abstract}" for p in papers]
    vectors = service.embed_batch(texts)

    for paper, vector in zip(papers, vectors):
        store.upsert_paper(
            paper_id=paper.id,
            vector=vector,
            payload={
                "title": paper.title,
                "source": paper.source_name,
                "conference": paper.conference,
            },
        )
        repo.mark_embedded(paper.id)
        print(f"  + embedding generated: {paper.title}")

    print(f"\nTotal points in Qdrant: {store.count()}")
    session.close()


if __name__ == "__main__":
    main()
