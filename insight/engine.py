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
        if optimized_query != question:
            logger.info(f"Query optimized: {question} -> {optimized_query}")
        
        # 0. Selection: Choose provider (Primary preferred)
        provider = self.primary
        if hasattr(provider, "is_available") and not provider.is_available():
            confirmed = await async_confirm("Primary LLM provider is unavailable. Switch to Fallback?")
            if not confirmed:
                return "Operation cancelled by user: Primary unavailable and Fallback rejected."
            provider = self.fallback

        # 1. Cache check (Fast path)
        cache_key = f"insight:{optimized_query}"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached:
                logger.info(f"Insight Cache Hit for key: {cache_key}")
                return cached
            logger.info(f"Insight Cache Miss for key: {cache_key}")

        # 2. Vector retrieval & Query Expansion
        logger.info(f"Retrieving Knowledge for: {optimized_query[:50]}...")
        
        # 2a. HyDE (Hypothetical Document Embedding)
        search_query = optimized_query
        if config.RAG_HYDE_ENABLED:
            search_query = await self.optimizer.get_hyde_query(optimized_query, llm=provider)
            logger.info(f"HyDE Answer Generated: {search_query[:50]}...")

        # 2b. Expand query (Multi-query search)
        queries = await self.optimizer.expand_query(search_query, llm=provider)
        
        all_docs = []
        seen_contents = set()
        
        for q in queries:
            docs = await self.retriever.retrieve(q)
            for d in docs:
                content = d.get("content", "")
                if content not in seen_contents:
                    all_docs.append(d)
                    seen_contents.add(content)
        
        if all_docs:
            logger.info(f"Retrieved {len(all_docs)} unique documents. Reranking...")
            # MMR Reranking
            docs = self.optimizer.rerank(all_docs, optimized_query)
            # Contextual Compression
            docs = self.optimizer.compress_context(docs, optimized_query)
        else:
            docs = []

        # 3. Prompt construction
        prompt = self.composer.build_prompt(optimized_query, docs)
        
        # Enforce input length limit
        if len(prompt.split()) > config.SECURITY_MAX_INPUT_LENGTH * 1.5: # Rough estimate
            # Very basic truncation for now
            prompt = prompt[:config.SECURITY_MAX_INPUT_LENGTH * 4]

        # 4. LLM Generation (with runtime fallback)
        try:
            response = await provider.generate(prompt)
        except Exception as e:
            logger.error(f"LLM provider failed: {e}")
            if provider == self.primary:
                confirmed = await async_confirm(f"Primary LLM failed ({e}). Switch to Fallback for this request?")
                if confirmed:
                    if hasattr(self.fallback, "is_available") and not self.fallback.is_available():
                        return f"Error: Secondary provider is not configured. Cannot fallback."
                    
                    logger.info("Retrying with secondary provider...")
                    try:
                        response = await self.fallback.generate(prompt)
                    except Exception as fallback_e:
                        return f"Error: Both primary and fallback providers failed.\nPrimary: {e}\nFallback: {fallback_e}"
                else:
                    return f"Error: Primary LLM failed and fallback was rejected. Details: {e}"
            else:
                raise e

        # 5. Response caching
        if self.cache:
            await self.cache.set(cache_key, response, ttl=300)

        return response
