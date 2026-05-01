import csv
from pathlib import Path

from models.schemas import Ticket, OutputRow


def read_tickets(csv_path: str | Path) -> list[Ticket]:
    tickets = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tickets.append(
                Ticket(
                    issue=row.get("Issue", row.get("issue", "")).strip(),
                    subject=row.get("Subject", row.get("subject", "")).strip(),
                    company=row.get("Company", row.get("company", "")).strip(),
                )
            )
    return tickets


def write_output(rows: list[OutputRow], csv_path: str | Path):
    fieldnames = [
        "issue",
        "subject",
        "company",
        "response",
        "product_area",
        "status",
        "request_type",
        "justification",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "issue": row.issue,
                    "subject": row.subject,
                    "company": row.company,
                    "response": row.response,
                    "product_area": row.product_area,
                    "status": row.status,
                    "request_type": row.request_type,
                    "justification": row.justification,
                }
            )
