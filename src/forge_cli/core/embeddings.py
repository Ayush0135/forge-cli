from abc import ABC, abstractmethod
from typing import Any


class EmbeddingProvider(ABC):
    """Abstract base class for embedding models."""
    
    @abstractmethod
    def generate_embedding(self, text: str) -> list[float]:
        pass
        
    @abstractmethod
    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        pass

class VectorStore(ABC):
    """Abstract base class for vector databases."""
    
    @abstractmethod
    def add_vector(self, id: str, vector: list[float], metadata: dict[str, Any]):
        pass
        
    @abstractmethod
    def search(self, vector: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        pass

class SemanticSearcher(ABC):
    """Abstract base class for combining embeddings and vector search."""
    
    @abstractmethod
    def index_document(self, id: str, text: str, metadata: dict[str, Any]):
        pass
        
    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        pass
