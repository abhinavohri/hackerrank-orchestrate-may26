from models.schemas import (
    Ticket,
    Article,
    Classification,
    EscalationDecision,
    ResponseOutput,
)
from services.llm.base import LLMService
from .base import ResponseService


class GroundedResponder(ResponseService):
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def generate(
        self,
        ticket: Ticket,
        context: list[Article],
        classification: Classification,
        escalation: EscalationDecision,
    ) -> ResponseOutput:
        _, response_output = self.llm_service.classify_and_respond(
            ticket=ticket,
            articles=context,
            force_escalate=escalation.should_escalate,
            escalation_reason=escalation.reason,
        )
        return response_output
