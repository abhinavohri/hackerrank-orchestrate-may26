import time

from google import genai

from config import GEMINI_API_KEY, EMBEDDING_MODEL, EMBEDDING_DIMENSION
from .base import EmbeddingService

MAX_CONTENT_WORDS = 1500
BATCH_SIZE = 5
RATE_LIMIT_DELAY = 5
RATE_LIMIT_SLEEP = 120


def _truncate(text: str, max_words: int = MAX_CONTENT_WORDS) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])


def _call_with_rate_limit_retry(fn):
    try:
        return fn()
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            print(f"  Rate limited: {e}")
            print(f"  Sleeping {RATE_LIMIT_SLEEP}s...")
            time.sleep(RATE_LIMIT_SLEEP)
            return fn()
        raise


class GeminiEmbeddingService(EmbeddingService):
    def __init__(self, api_key: str = "", model: str = ""):
        self.model = model or EMBEDDING_MODEL
        self.client = genai.Client(api_key=api_key or GEMINI_API_KEY)

    def embed_document(self, title: str, content: str) -> list[float]:
        doc_text = f"title: {title} | text: {_truncate(content)}"

        def _call():
            return self.client.models.embed_content(
                model=self.model,
                contents=doc_text,
                config={"output_dimensionality": EMBEDDING_DIMENSION},
            )

        result = _call_with_rate_limit_retry(_call)
        return list(result.embeddings[0].values)

    def embed_query(self, query: str) -> list[float]:
        query_text = f"task: question answering | query: {query}"

        def _call():
            return self.client.models.embed_content(
                model=self.model,
                contents=query_text,
                config={"output_dimensionality": EMBEDDING_DIMENSION},
            )

        result = _call_with_rate_limit_retry(_call)
        return list(result.embeddings[0].values)

    def embed_documents_batch(
        self, documents: list[dict[str, str]]
    ) -> list[list[float]]:
        all_embeddings = []
        for i in range(0, len(documents), BATCH_SIZE):
            batch = documents[i : i + BATCH_SIZE]
            texts = [
                f"title: {doc['title']} | text: {_truncate(doc['content'])}"
                for doc in batch
            ]

            def _call(t=texts):
                return self.client.models.embed_content(
                    model=self.model,
                    contents=t,
                    config={"output_dimensionality": EMBEDDING_DIMENSION},
                )

            results = _call_with_rate_limit_retry(_call)
            for emb in results.embeddings:
                all_embeddings.append(list(emb.values))

            done = min(i + BATCH_SIZE, len(documents))
            print(f"  Embedded {done}/{len(documents)} documents...")

            if i + BATCH_SIZE < len(documents):
                time.sleep(RATE_LIMIT_DELAY)

        return all_embeddings
