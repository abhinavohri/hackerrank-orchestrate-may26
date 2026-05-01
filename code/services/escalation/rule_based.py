import re

from models.schemas import Ticket, Article, EscalationDecision
from .base import EscalationService

ESCALATION_PATTERNS = [
    (r"site\s+(is\s+)?down", "Service outage reported"),
    (r"all\s+requests?\s+(are\s+)?failing", "Service outage reported"),
    (r"(completely|totally)\s+(stopped|broken|down)", "Service outage reported"),
    (r"not\s+working\s+at\s+all", "Service outage reported"),
    (r"none\s+of\s+the\s+(pages|submissions|features)\s+(are\s+)?working", "Widespread service failure reported"),
    (r"order\s*(id|#|number)?\s*[:=]?\s*\w+", "Billing issue with specific order reference"),
    (r"cs_live_\w+", "Billing issue with specific transaction ID"),
    (r"refund", "Refund request requires human authorization"),
    (r"restore\s+(my\s+)?access", "Access restoration requires admin intervention"),
    (r"increase\s+(my\s+)?score", "Score modification requires human review"),
    (r"review\s+my\s+answers", "Assessment review requires human intervention"),
    (r"ban\s+the\s+(seller|merchant)", "Merchant action requires human authorization"),
    (r"pause\s+(our\s+|my\s+)?subscription", "Subscription changes require account management"),
    (r"reschedul", "Rescheduling requires coordination with hiring company"),
    (r"identity\s+(has\s+been\s+)?stolen", "Identity theft requires urgent human intervention"),
    (r"payment\s+issue.*order", "Payment dispute requires human investigation"),
]

VAGUE_PATTERNS = [
    r"^(it'?s\s+)?not\s+working[,.]?\s*(help)?$",
    r"^help\s*(me)?$",
    r"^(please\s+)?fix\s+(it|this)$",
]


class RuleBasedEscalation(EscalationService):
    def should_escalate(
        self, ticket: Ticket, retrieved_docs: list[Article]
    ) -> EscalationDecision:
        text = f"{ticket.subject} {ticket.issue}".lower().strip()

        for pattern, reason in ESCALATION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return EscalationDecision(should_escalate=True, reason=reason)

        company = (ticket.company or "").strip().lower()
        if company in ("", "none"):
            for pattern in VAGUE_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    return EscalationDecision(
                        should_escalate=True,
                        reason="Ticket is too vague with no company context to provide meaningful assistance",
                    )

        return EscalationDecision(should_escalate=False, reason="")
