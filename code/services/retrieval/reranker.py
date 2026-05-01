from models.schemas import Ticket, RetrievalResult, Article
from services.llm.base import LLMService


class Reranker:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def rerank(
        self,
        ticket: Ticket,
        results: list[RetrievalResult],
        top_k: int = 5,
    ) -> list[RetrievalResult]:
        if len(results) <= top_k:
            return results

        articles = [r.article for r in results]
        reranked_articles = self.llm_service.rerank(ticket, articles, top_k=top_k)

        article_id_to_result = {r.article.id: r for r in results}
        reranked_results = []
        for i, article in enumerate(reranked_articles):
            if article.id in article_id_to_result:
                original = article_id_to_result[article.id]
                reranked_results.append(
                    RetrievalResult(article=original.article, score=1.0 - (i * 0.1))
                )

        return reranked_results
