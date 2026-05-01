from models.schemas import Ticket, OutputRow, RetrievalResult
from services.retrieval.base import RetrievalService
from services.retrieval.reranker import Reranker
from services.escalation.base import EscalationService
from services.llm.base import LLMService
from config import TOP_K_RETRIEVAL, TOP_K_FINAL


class PipelineOrchestrator:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        escalation_service: EscalationService,
        llm_service: LLMService,
        reranker: Reranker | None = None,
    ):
        self.retrieval_service = retrieval_service
        self.escalation_service = escalation_service
        self.llm_service = llm_service
        self.reranker = reranker

    def process_ticket(self, ticket: Ticket) -> OutputRow:
        results = self.retrieval_service.retrieve(ticket, top_k=TOP_K_RETRIEVAL)

        if self.reranker and len(results) > TOP_K_FINAL:
            results = self.reranker.rerank(ticket, results, top_k=TOP_K_FINAL)
        else:
            results = results[:TOP_K_FINAL]

        articles = [r.article for r in results]

        escalation = self.escalation_service.should_escalate(ticket, articles)

        classification, response_output = self.llm_service.classify_and_respond(
            ticket=ticket,
            articles=articles,
            force_escalate=escalation.should_escalate,
            escalation_reason=escalation.reason,
        )

        return OutputRow(
            issue=ticket.issue,
            subject=ticket.subject,
            company=ticket.company,
            response=response_output.response,
            product_area=classification.product_area,
            status=classification.status,
            request_type=classification.request_type,
            justification=response_output.justification,
        )
