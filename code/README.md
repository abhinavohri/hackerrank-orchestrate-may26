# Support Ticket Triage Agent

A multi-domain AI agent that triages support tickets across HackerRank, Claude, and Visa ecosystems using RAG (Retrieval-Augmented Generation) with a local support corpus.

## Architecture

Decoupled services pipeline:
- **Corpus Loader** - parses 774 markdown support articles with metadata
- **Embedding Service** - Gemini embedding-2 with asymmetric task prefixes
- **Vector Store** - pgvector on Supabase for similarity search with domain filtering
- **Retrieval Service** - cosine similarity + LLM-based re-ranking
- **Escalation Service** - rule-based detection of high-risk tickets
- **LLM Service** - Gemini 2.5 Flash for classification and grounded response generation
- **Pipeline Orchestrator** - ties all services together per ticket

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill in environment variables
cp ../.env.example ../.env
# Edit .env with your GEMINI_API_KEY and SUPABASE_DB_URL

# One-time: ingest corpus into pgvector
python3 scripts/ingest_corpus.py

# Run the agent on all tickets
python3 main.py

# Validate against labeled samples
python3 scripts/validate_samples.py
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key |
| `SUPABASE_DB_URL` | PostgreSQL connection string for Supabase with pgvector |
| `EMBEDDING_MODEL` | Embedding model (default: `gemini-embedding-2`) |
| `LLM_MODEL` | LLM model (default: `gemini-2.5-flash`) |

## Output

Produces `support_tickets/output.csv` with columns:
`issue, subject, company, response, product_area, status, request_type, justification`
