import json

import psycopg2
from pgvector.psycopg2 import register_vector

from config import SUPABASE_DB_URL
from models.schemas import Article, RetrievalResult
from .base import VectorStoreService


class PgVectorStore(VectorStoreService):
    def __init__(self, db_url: str = ""):
        self.db_url = db_url or SUPABASE_DB_URL
        self.conn = psycopg2.connect(self.db_url)
        self.conn.autocommit = True
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(self.conn)

    def create_table(self):
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,
                    domain TEXT NOT NULL,
                    product_area TEXT NOT NULL,
                    title TEXT,
                    breadcrumbs TEXT,
                    source_url TEXT,
                    content TEXT,
                    path TEXT,
                    embedding vector(768),
                    metadata JSONB
                )
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS articles_embedding_idx
                ON articles USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 20)
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS articles_domain_idx
                ON articles (domain)
                """
            )

    def upsert(self, articles: list[Article], embeddings: list[list[float]]):
        with self.conn.cursor() as cur:
            for article, embedding in zip(articles, embeddings):
                cur.execute(
                    """
                    INSERT INTO articles (id, domain, product_area, title, breadcrumbs, source_url, content, path, embedding, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::vector, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        domain = EXCLUDED.domain,
                        product_area = EXCLUDED.product_area,
                        title = EXCLUDED.title,
                        breadcrumbs = EXCLUDED.breadcrumbs,
                        source_url = EXCLUDED.source_url,
                        content = EXCLUDED.content,
                        path = EXCLUDED.path,
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata
                    """,
                    (
                        article.id,
                        article.domain,
                        article.product_area,
                        article.title,
                        json.dumps(article.breadcrumbs),
                        article.source_url,
                        article.content,
                        article.path,
                        str(embedding),
                        json.dumps(article.metadata),
                    ),
                )

    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        domain_filter: str | None = None,
    ) -> list[RetrievalResult]:
        embedding_str = str(query_embedding)

        if domain_filter:
            query = """
                SELECT id, domain, product_area, title, breadcrumbs, source_url, content, path, metadata,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM articles
                WHERE domain = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """
            params = (embedding_str, domain_filter, embedding_str, top_k)
        else:
            query = """
                SELECT id, domain, product_area, title, breadcrumbs, source_url, content, path, metadata,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM articles
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """
            params = (embedding_str, embedding_str, top_k)

        results = []
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            for row in cur.fetchall():
                breadcrumbs = json.loads(row[4]) if row[4] else []
                metadata = json.loads(row[8]) if isinstance(row[8], str) else (row[8] or {})
                article = Article(
                    id=row[0],
                    domain=row[1],
                    product_area=row[2],
                    title=row[3] or "",
                    breadcrumbs=breadcrumbs,
                    source_url=row[5] or "",
                    content=row[6] or "",
                    path=row[7] or "",
                    metadata=metadata,
                )
                results.append(RetrievalResult(article=article, score=float(row[9])))

        return results

    def get_article_count(self) -> int:
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM articles")
            return cur.fetchone()[0]

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
