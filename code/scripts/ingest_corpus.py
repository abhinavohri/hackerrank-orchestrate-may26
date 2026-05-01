"""One-time script: load articles, embed them, store in pgvector.

Embeds and stores one batch at a time so progress is saved incrementally.
On restart, skips articles already in the DB and re-processes the last
successful batch as a safety margin.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.corpus_loader import load_all_articles
from services.embedding import GeminiEmbeddingService
from services.vector_store import PgVectorStore

EMBED_BATCH_SIZE = 5


def get_existing_ids(store: PgVectorStore) -> set[str]:
    with store.conn.cursor() as cur:
        cur.execute("SELECT id FROM articles")
        return {row[0] for row in cur.fetchall()}


def main():
    print("=== Corpus Ingestion Pipeline ===\n")

    print("1. Loading articles from corpus...")
    articles = load_all_articles()
    print(f"   Loaded {len(articles)} articles\n")

    print("2. Initializing vector store (pgvector on Supabase)...")
    store = PgVectorStore()
    store.create_table()

    existing_ids = get_existing_ids(store)
    stored_count = len(existing_ids)
    print(f"   Already ingested: {stored_count} articles")

    new_articles = [a for a in articles if a.id not in existing_ids]

    # Re-process last batch as safety margin (upsert is idempotent)
    overlap = EMBED_BATCH_SIZE
    if stored_count > 0 and new_articles:
        already_done = [a for a in articles if a.id in existing_ids]
        redo = already_done[-overlap:]
        new_articles = redo + new_articles
        print(f"   Re-processing last {len(redo)} articles as safety overlap")

    if not new_articles:
        print("   All articles already ingested. Nothing to do.")
        store.close()
        return

    print(f"   Articles to process: {len(new_articles)}\n")

    print("3. Embedding and storing batch-by-batch...\n")
    embedder = GeminiEmbeddingService()
    total = len(new_articles)

    for i in range(0, total, EMBED_BATCH_SIZE):
        batch = new_articles[i : i + EMBED_BATCH_SIZE]
        docs = [{"title": a.title, "content": a.content} for a in batch]

        embeddings = embedder.embed_documents_batch(docs)
        store.upsert(batch, embeddings)

        done = min(i + EMBED_BATCH_SIZE, total)
        db_count = store.get_article_count()
        print(f"   Batch done: {done}/{total} processed | {db_count} total in DB\n")

    final_count = store.get_article_count()
    print(f"=== Done! {final_count} articles stored in pgvector ===")

    store.close()


if __name__ == "__main__":
    main()
