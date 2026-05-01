from dataclasses import dataclass, field


@dataclass
class Article:
    id: str
    path: str
    domain: str
    title: str
    content: str
    product_area: str
    breadcrumbs: list[str] = field(default_factory=list)
    source_url: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class Ticket:
    issue: str
    subject: str
    company: str


@dataclass
class RetrievalResult:
    article: Article
    score: float


@dataclass
class Classification:
    request_type: str
    product_area: str
    status: str


@dataclass
class EscalationDecision:
    should_escalate: bool
    reason: str


@dataclass
class ResponseOutput:
    response: str
    justification: str


@dataclass
class OutputRow:
    issue: str
    subject: str
    company: str
    response: str
    product_area: str
    status: str
    request_type: str
    justification: str
