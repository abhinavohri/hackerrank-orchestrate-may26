from abc import ABC, abstractmethod
from models.schemas import Ticket, Article, Classification, ResponseOutput


class LLMService(ABC):
    @abstractmethod
    def classify_and_respond(
        self,
        ticket: Ticket,
        articles: list[Article],
        force_escalate: bool = False,
        escalation_reason: str = "",
    ) -> tuple[Classification, ResponseOutput]:
        """Classify a ticket and generate a grounded response in one call."""

    @abstractmethod
    def rerank(
        self, ticket: Ticket, articles: list[Article], top_k: int = 5
    ) -> list[Article]:
        """Re-rank articles by relevance to the ticket."""
