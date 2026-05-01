from models.schemas import Ticket, RetrievalResult
from services.embedding.base import EmbeddingService
from services.vector_store.base import VectorStoreService
from .base import RetrievalService

COMPANY_TO_DOMAIN = {
    "HackerRank": "hackerrank",
    "Claude": "claude",
    "Visa": "visa",
}


class CosineRetriever(RetrievalService):
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStoreService,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def retrieve(self, ticket: Ticket, top_k: int = 10) -> list[RetrievalResult]:
        query = f"{ticket.subject} {ticket.issue}".strip()
        query_embedding = self.embedding_service.embed_query(query)

        domain_filter = None
        company = ticket.company.strip() if ticket.company else ""
        if company and company.lower() != "none":
            domain_filter = COMPANY_TO_DOMAIN.get(company)

        results = self.vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k,
            domain_filter=domain_filter,
        )

        return results
