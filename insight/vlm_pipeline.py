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
    def __init__(self, primary, fallback, vector_db=None, cache=None):
        self.primary = primary
        self.fallback = fallback
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

    async def ask(self, prompt: str, image_path: str, use_rag: bool = False, session_id: Optional[str] = None) -> str:
        """
        Ask a question about an image, optionally using RAG for context.
        """
        # 1. Selection: Choose provider (Primary preferred if available)
        provider = self.primary
        if hasattr(provider, "is_available") and not provider.is_available():
            confirmed = await async_confirm("Primary VLM provider is unavailable. Switch to Fallback?")
            if not confirmed:
                return "Operation cancelled by user: Primary unavailable and Fallback rejected."
            
            logger.warning("Falling back to secondary VLM provider.")
            provider = self.fallback

        # 2. Caching
        cache_key = self._get_cache_key(prompt, image_path)
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached:
                logger.info(f"VLM Cache Hit for key: {cache_key}")
                return cached
            logger.info(f"VLM Cache Miss for key: {cache_key}")

        # 3. RAG Context Injection
        final_prompt = prompt
        if use_rag and self.retriever:
            logger.info(f"Retrieving RAG context for prompt: {prompt[:50]}...")
            # Retrieve text context relevant to the prompt
            docs = await self.retriever.retrieve(prompt)
            if docs:
                context_parts = []
                for d in docs[:3]:
                    content = d.get("content", str(d)) if isinstance(d, dict) else str(d)
                    context_parts.append(content)
                context_str = "\n".join(context_parts)
                logger.info(f"Injected {len(docs)} documents into VLM prompt.")
                final_prompt = f"Context from database:\n{context_str}\n\nUser Question: {prompt}"

        # 4. VLM Generation (with runtime fallback)
        try:
            response = await provider.generate_with_image(final_prompt, image_path, session_id=session_id)
        except Exception as e:
            logger.error(f"VLM provider failed: {e}")
            if provider == self.primary:
                confirmed = await async_confirm(f"Primary VLM failed ({e}). Switch to Fallback for this request?")
                if confirmed:
                    if hasattr(self.fallback, "is_available") and not self.fallback.is_available():
                        return f"Error: Secondary provider is not configured. Cannot fallback."
                    
                    logger.info("Retrying with secondary provider...")
                    try:
                        response = await self.fallback.generate_with_image(final_prompt, image_path, session_id=session_id)
                    except Exception as fallback_e:
                        return f"Error: Both primary and fallback providers failed.\nPrimary: {e}\nFallback: {fallback_e}"
                else:
                    return f"Error: Primary VLM failed and fallback was rejected. Details: {e}"
            else:
                raise e

        # 5. Save to Cache
        if self.cache:
            await self.cache.set(cache_key, response, ttl=3600)

        return response
