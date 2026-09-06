from abc import ABC, abstractmethod
from app.models.paper import SearchResult

class BaseCollector(ABC):
    """Toda fonte de busca (Arxiv, Semantic Scholar, etc.) implementa essa interface."""
    @abstractmethod
    def search(self, query: str, max_results: int = 20) -> SearchResult:
        """Busca papers pela query e retorna um SearchResult padronizado."""
        raise NotImplementedError

