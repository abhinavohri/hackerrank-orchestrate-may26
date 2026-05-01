from abc import ABC, abstractmethod
from models.schemas import Ticket, Article, EscalationDecision


class EscalationService(ABC):
    @abstractmethod
    def should_escalate(
        self, ticket: Ticket, retrieved_docs: list[Article]
    ) -> EscalationDecision:
        """Determine whether a ticket should be escalated to a human."""
