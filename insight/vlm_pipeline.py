import hashlib
import os
from typing import Optional
from IRYM_sdk.insight.retriever import VectorRetriever
from IRYM_sdk.insight.composer import PromptComposer

class VLMPipeline:
    """
    High-level orchestration for Vision-Language Models.
    Integrates VLM, RAG context, and Caching in a unified interface.
    """
    def __init__(self, vlm, vector_db=None, cache=None):
        self.vlm = vlm
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
        # 1. Caching
        cache_key = self._get_cache_key(prompt, image_path)
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

        # 2. RAG Context Injection
        final_prompt = prompt
        if use_rag and self.retriever:
            # Retrieve text context relevant to the prompt
            docs = await self.retriever.retrieve(prompt)
            if docs:
                context_str = "\n".join([d.page_content for d in docs[:3]])
                final_prompt = f"Context from database:\n{context_str}\n\nUser Question: {prompt}"

        # 3. VLM Generation
        response = await self.vlm.generate_with_image(final_prompt, image_path)

        # 4. Save to Cache
        if self.cache:
            await self.cache.set(cache_key, response, ttl=3600)

        return response
