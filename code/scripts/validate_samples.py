"""Validate the pipeline against sample_support_tickets.csv with known expected outputs."""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import SAMPLE_CSV
from utils.csv_io import read_tickets
from services.embedding import GeminiEmbeddingService
from services.vector_store import PgVectorStore
from services.retrieval import CosineRetriever
from services.retrieval.reranker import Reranker
from services.escalation import RuleBasedEscalation
from services.llm import GeminiLLMService
from pipeline.orchestrator import PipelineOrchestrator
from pipeline.batch_runner import run_batch


def load_expected(csv_path: str) -> list[dict]:
    expected = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            expected.append(
                {
                    "status": row.get("Status", row.get("status", "")).strip().lower(),
                    "request_type": row.get("Request Type", row.get("request_type", "")).strip().lower(),
                    "product_area": row.get("Product Area", row.get("product_area", "")).strip().lower(),
                }
            )
    return expected


def main():
    print("=== Validating against sample tickets ===\n")

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

    tickets = read_tickets(SAMPLE_CSV)
    expected = load_expected(str(SAMPLE_CSV))

    results = run_batch(orchestrator, tickets)

    print("\n=== Accuracy Report ===\n")
    fields = ["status", "request_type", "product_area"]
    correct = {f: 0 for f in fields}
    total = len(results)

    for i, (result, exp) in enumerate(zip(results, expected)):
        print(f"\nTicket {i+1}: {result.subject or result.issue[:50]}")
        for field in fields:
            actual = getattr(result, field).strip().lower()
            exp_val = exp[field]
            match = actual == exp_val
            if match:
                correct[field] += 1
            status = "OK" if match else "MISMATCH"
            print(f"  {field}: {actual} vs {exp_val} [{status}]")

    print(f"\n--- Summary ({total} tickets) ---")
    for field in fields:
        pct = (correct[field] / total * 100) if total else 0
        print(f"  {field}: {correct[field]}/{total} ({pct:.0f}%)")

    store.close()


if __name__ == "__main__":
    main()
