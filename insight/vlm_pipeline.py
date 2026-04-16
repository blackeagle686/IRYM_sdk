import hashlib
import os
from typing import Optional
from IRYM_sdk.insight.retriever import VectorRetriever
from IRYM_sdk.insight.composer import PromptComposer
from IRYM_sdk.observability.logger import get_logger
from IRYM_sdk.core.utils import async_confirm

logger = get_logger("IRYM.VLM")

class VLMPipeline:
    """
    High-level orchestration for Vision-Language Models.
    Integrates VLM, RAG context, and Caching in a unified interface.
    """
    def __init__(self, vlm_openai, vlm_local, vector_db=None, cache=None):
        self.vlm_openai = vlm_openai
        self.vlm_local = vlm_local
        self.vector_db = vector_db
        self.cache = cache
        
        self.retriever = VectorRetriever(vector_db) if vector_db else None
        self.composer = PromptComposer()

    def _get_cache_key(self, prompt: str, image_path: str) -> str:
        # Create a unique key based on prompt and image content (simplified to path + stats for speed)
        # or just path + hash of prompt
        try:
            mtime = os.path.getmtime(image_path)
            size = os.path.getsize(image_path)
            combined = f"{prompt}:{image_path}:{mtime}:{size}"
            return f"vlm_cache:{hashlib.md5(combined.encode()).hexdigest()}"
        except Exception:
            # Fallback if file access fails
            return f"vlm_cache:{hashlib.md5((prompt + image_path).encode()).hexdigest()}"

    async def ask(self, prompt: str, image_path: str, use_rag: bool = False) -> str:
        """
        Ask a question about an image, optionally using RAG for context.
        """
        # 1. Selection: Choose provider (OpenAI preferred if available)
        provider = self.vlm_openai
        if not provider.is_available():
            confirmed = await async_confirm("OpenAI VLM is unavailable. Switch to Local VLM?")
            if not confirmed:
                return "Operation cancelled by user: OpenAI unavailable and Local fallback rejected."
            
            logger.warning("Falling back to Local VLM as requested.")
            provider = self.vlm_local

        # 2. Caching
        cache_key = self._get_cache_key(prompt, image_path)
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

        # 3. RAG Context Injection
        final_prompt = prompt
        if use_rag and self.retriever:
            # Retrieve text context relevant to the prompt
            docs = await self.retriever.retrieve(prompt)
            if docs:
                context_str = "\n".join([d.page_content for d in docs[:3]])
                final_prompt = f"Context from database:\n{context_str}\n\nUser Question: {prompt}"

        # 4. VLM Generation
        response = await provider.generate_with_image(final_prompt, image_path)

        # 5. Save to Cache
        if self.cache:
            await self.cache.set(cache_key, response, ttl=3600)

        return response
