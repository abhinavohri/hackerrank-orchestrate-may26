from abc import ABC, abstractmethod


class EmbeddingService(ABC):
    @abstractmethod
    def embed_document(self, title: str, content: str) -> list[float]:
        """Embed a document (article) for storage."""

    @abstractmethod
    def embed_query(self, query: str) -> list[float]:
        """Embed a query (ticket) for retrieval."""

    @abstractmethod
    def embed_documents_batch(
        self, documents: list[dict[str, str]]
    ) -> list[list[float]]:
        """Embed multiple documents. Each dict has 'title' and 'content' keys."""
