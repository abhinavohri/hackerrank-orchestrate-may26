from abc import ABC, abstractmethod
from models.schemas import Ticket, RetrievalResult


class RetrievalService(ABC):
    @abstractmethod
    def retrieve(self, ticket: Ticket, top_k: int = 5) -> list[RetrievalResult]:
        """Retrieve the most relevant articles for a given ticket."""
