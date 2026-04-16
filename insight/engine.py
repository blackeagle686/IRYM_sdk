from IRYM_sdk.insight.base import BaseInsightService
from IRYM_sdk.insight.retriever import VectorRetriever
from IRYM_sdk.insight.composer import PromptComposer
from IRYM_sdk.insight.optimizer import Optimizer
from typing import Optional
from IRYM_sdk.core.utils import async_confirm
from IRYM_sdk.observability.logger import get_logger

logger = get_logger("IRYM.Insight")

class InsightEngine(BaseInsightService):
    """
    Main orchestration layer.
    Manages vector retrieval, prompt building, LLM generation, and cache checking.
    """
    def __init__(self, vector_db, primary, fallback, cache=None):
        self.vector_db = vector_db
        self.primary = primary
        self.fallback = fallback
        self.cache = cache
        
        self.retriever = VectorRetriever(vector_db)
        self.composer = PromptComposer()
        self.optimizer = Optimizer()

    async def init(self):
        pass

    async def query(self, question: str, context: Optional[dict] = None):
        optimized_query = self.optimizer.rewrite_query(question)
        
        # 0. Selection: Choose provider (Primary preferred)
        provider = self.primary
        if hasattr(provider, "is_available") and not provider.is_available():
            confirmed = await async_confirm("Primary LLM provider is unavailable. Switch to Fallback?")
            if not confirmed:
                return "Operation cancelled by user: Primary unavailable and Fallback rejected."
            provider = self.fallback

        # 1. Cache check (Fast path)
        if self.cache:
            cached = await self.cache.get(f"insight:{optimized_query}")
            if cached:
                return cached

        # 2. Vector retrieval & reranking
        docs = await self.retriever.retrieve(optimized_query)
        docs = self.optimizer.rerank(docs, optimized_query)

        # 3. Prompt construction
        prompt = self.composer.build_prompt(optimized_query, docs)

        # 4. LLM Generation (with runtime fallback)
        try:
            response = await provider.generate(prompt)
        except Exception as e:
            logger.error(f"LLM provider failed: {e}")
            if provider == self.primary:
                confirmed = await async_confirm(f"Primary LLM failed ({e}). Switch to Fallback for this request?")
                if confirmed:
                    logger.info("Retrying with secondary provider...")
                    response = await self.fallback.generate(prompt)
                else:
                    return f"Error: Primary LLM failed and fallback was rejected. Details: {e}"
            else:
                raise e

        # 5. Response caching
        if self.cache:
            await self.cache.set(f"insight:{optimized_query}", response, ttl=300)

        return response
