from models.schemas import Ticket, OutputRow
from pipeline.orchestrator import PipelineOrchestrator


def run_batch(
    orchestrator: PipelineOrchestrator,
    tickets: list[Ticket],
) -> list[OutputRow]:
    results = []
    for i, ticket in enumerate(tickets, 1):
        print(f"\n[{i}/{len(tickets)}] Processing: {ticket.subject or ticket.issue[:60]}...")
        try:
            result = orchestrator.process_ticket(ticket)
            print(f"  -> {result.status} | {result.request_type} | {result.product_area}")
            results.append(result)
        except Exception as e:
            print(f"  -> ERROR: {e}")
            results.append(
                OutputRow(
                    issue=ticket.issue,
                    subject=ticket.subject,
                    company=ticket.company,
                    response="We are unable to process your request at this time. Please contact support directly.",
                    product_area="general_support",
                    status="escalated",
                    request_type="product_issue",
                    justification=f"Processing error: {e}",
                )
            )
    return results
