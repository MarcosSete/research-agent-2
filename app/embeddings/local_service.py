from sentence_transformers import SentenceTransformer
from app.embeddings.base import BaseEmbeddingService

MODEL_NAME = "all-mpnet-base-v2"

class LocalEmbeddingService(BaseEmbeddingService):
    def __init__(self):
        self._model = SentenceTransformer(MODEL_NAME)

    def embed(self, text: str) -> list[float]:
        vector = self._model.encode(text)
        return vector.tolist()


    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts)
        return vectors.tolist()



    @property
    def dimension(self) -> int:
        return self._model.get_embedding_dimension()