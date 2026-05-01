from abc import ABC, abstractmethod
from models.schemas import (
    Ticket,
    Article,
    Classification,
    EscalationDecision,
    ResponseOutput,
)


class ResponseService(ABC):
    @abstractmethod
    def generate(
        self,
        ticket: Ticket,
        context: list[Article],
        classification: Classification,
        escalation: EscalationDecision,
    ) -> ResponseOutput:
        """Generate a grounded response for the ticket."""
