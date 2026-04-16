from IRYM_sdk.insight.base import BaseInsightService
from IRYM_sdk.insight.retriever import VectorRetriever
from IRYM_sdk.insight.composer import PromptComposer
from IRYM_sdk.insight.optimizer import Optimizer
from typing import Optional
from IRYM_sdk.core.utils import async_confirm

class InsightEngine(BaseInsightService):
    """
    Main orchestration layer.
    Manages vector retrieval, prompt building, LLM generation, and cache checking.
    """
    def __init__(self, vector_db, llm_openai, llm_local, cache=None):
        self.vector_db = vector_db
        self.llm_openai = llm_openai
        self.llm_local = llm_local
        self.cache = cache
        
        self.retriever = VectorRetriever(vector_db)
        self.composer = PromptComposer()
        self.optimizer = Optimizer()

    async def init(self):
        pass

    async def query(self, question: str, context: Optional[dict] = None):
        optimized_query = self.optimizer.rewrite_query(question)
        
        # 0. Selection: Choose provider (OpenAI preferred)
        provider = self.llm_openai
        if hasattr(provider, "is_available") and not provider.is_available():
            confirmed = await async_confirm("OpenAI LLM is unavailable. Switch to Local LLM?")
            if not confirmed:
                return "Operation cancelled by user: OpenAI unavailable and Local fallback rejected."
            provider = self.llm_local

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

        # 4. LLM Generation
        response = await provider.generate(prompt)

        # 5. Response caching
        if self.cache:
            await self.cache.set(f"insight:{optimized_query}", response, ttl=300)

        return response
