"""Entry point: process all support tickets and generate output.csv."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import INPUT_CSV, OUTPUT_CSV, GEMINI_API_KEY, SUPABASE_DB_URL
from utils.csv_io import read_tickets, write_output
from services.embedding import GeminiEmbeddingService
from services.vector_store import PgVectorStore
from services.retrieval import CosineRetriever
from services.retrieval.reranker import Reranker
from services.escalation import RuleBasedEscalation
from services.llm import GeminiLLMService
from pipeline.orchestrator import PipelineOrchestrator
from pipeline.batch_runner import run_batch


def main():
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY environment variable is not set.")
        sys.exit(1)
    if not SUPABASE_DB_URL:
        print("ERROR: SUPABASE_DB_URL environment variable is not set.")
        sys.exit(1)

    print("=== Support Ticket Triage Agent ===\n")

    print("Initializing services...")
    embedder = GeminiEmbeddingService()
    store = PgVectorStore()
    retriever = CosineRetriever(embedder, store)
    llm = GeminiLLMService()
    reranker = Reranker(llm)
    escalation = RuleBasedEscalation()

    orchestrator = PipelineOrchestrator(
        retrieval_service=retriever,
        escalation_service=escalation,
        llm_service=llm,
        reranker=reranker,
    )

    print(f"Reading tickets from {INPUT_CSV}...")
    tickets = read_tickets(INPUT_CSV)
    print(f"Found {len(tickets)} tickets to process\n")

    results = run_batch(orchestrator, tickets)

    write_output(results, OUTPUT_CSV)
    print(f"\n=== Done! Output written to {OUTPUT_CSV} ===")
    print(f"Processed {len(results)} tickets: "
          f"{sum(1 for r in results if r.status == 'replied')} replied, "
          f"{sum(1 for r in results if r.status == 'escalated')} escalated")

    store.close()


if __name__ == "__main__":
    main()
