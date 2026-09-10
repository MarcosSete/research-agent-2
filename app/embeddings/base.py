from abc import ABC, abstractclassmethod


class BaseEmbeddingService(ABC):
    """Toda fonte de embeddings (local, OpenAI, etc.) implementa essa interface."""

    @abstractclassmethod
    def embed(self, text: str) -> list[float]:
        """Transforma um texto em um vetor de números."""
        raise NotImplementedError


    @abstractclassmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Transforma vários textos de uma vez (mais eficiente que chamar embed() em loop)."""
        raise NotImplementedError

    @property
    @abstractclassmethod
    def dimension(self) -> int:
        """Quantos números tem cada vetor gerado por esse modelo."""
        raise NotImplementedError