from IRYM_sdk.insight.base import BaseInsightService
from IRYM_sdk.insight.retriever import VectorRetriever
from IRYM_sdk.insight.composer import PromptComposer
from IRYM_sdk.insight.optimizer import Optimizer
from typing import Optional

class InsightEngine(BaseInsightService):
    """
    Main orchestration layer.
    Manages vector retrieval, prompt building, LLM generation, and cache checking.
    """
    def __init__(self, vector_db, llm, cache=None):
        self.vector_db = vector_db
        self.llm = llm
        self.cache = cache
        
        self.retriever = VectorRetriever(vector_db)
        self.composer = PromptComposer()
        self.optimizer = Optimizer()

    async def init(self):
        # Engine is stateless locally outside of assigned properties
        pass

    async def query(self, question: str, context: Optional[dict] = None):
        optimized_query = self.optimizer.rewrite_query(question)
        
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
        response = await self.llm.generate(prompt)

        # 5. Response caching
        if self.cache:
            await self.cache.set(f"insight:{optimized_query}", response, ttl=300)

        return response
