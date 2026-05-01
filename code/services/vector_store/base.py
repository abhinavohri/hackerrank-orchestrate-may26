from abc import ABC, abstractmethod
from models.schemas import Article, RetrievalResult


class VectorStoreService(ABC):
    @abstractmethod
    def create_table(self):
        """Create the articles table with vector column."""

    @abstractmethod
    def upsert(self, articles: list[Article], embeddings: list[list[float]]):
        """Insert or update articles with their embeddings."""

    @abstractmethod
    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        domain_filter: str | None = None,
    ) -> list[RetrievalResult]:
        """Search for similar articles by embedding vector."""

    @abstractmethod
    def close(self):
        """Close the database connection."""
