from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config.settings import settings

COLLECTION_NAME = "papers"


class QdrantStore:
    def __init__(self, vector_dimension: int):
        self.client = QdrantClient(url=settings.qdrant_url)
        self.vector_dimension = vector_dimension
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create the collection if it does not exist yet."""
        existing = self.client.get_collections().collections
        names = [c.name for c in existing]

        if COLLECTION_NAME not in names:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.vector_dimension,
                    distance=Distance.COSINE,
                )
            )

    def upsert_paper(self, paper_id: int, vector: list[float], payload: dict) -> None:
        """Store or update a paper vector. paper_id comes from PostgreSQL."""
        point = PointStruct(
            id=paper_id,
            vector=vector,
            payload=payload,
        )

        self.client.upsert(collection_name=COLLECTION_NAME, points=[point])

    def search_similar(self, vector: list[float], limit: int = 5) -> list[dict]:
        """Search for similar papers and return their stored vectors as well."""
        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=limit,
            with_vectors=True,
        ).points

        return [
            {
                "id": r.id,
                "score": r.score,
                "payload": r.payload,
                "vector": r.vector,
            }
            for r in results
        ]

    def count(self) -> int:
        info = self.client.get_collection(COLLECTION_NAME)
        return info.points_count
