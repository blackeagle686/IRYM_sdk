from phoenix.llm.base import BaseLLM
from phoenix.core.config import config
from openai import AsyncOpenAI
from phoenix.observability.tracing import tracer
from phoenix.observability.logger import get_logger
from phoenix.core.container import container
from typing import Optional

logger = get_logger("Phoenix AI.LLM.OpenAI")

class OpenAILLM(BaseLLM):
    def __init__(self):
        self.api_key = getattr(config, "OPENAI_API_KEY", None)
        self.base_url = getattr(config, "OPENAI_BASE_URL", None)
        self.model = getattr(config, "OPENAI_LLM_MODEL", None) or "LongCat-Flash-Chat"
        self.client = None

    def is_available(self) -> bool:
        # LongCat keys often start with 'ak_', standard OpenAI keys start with 'sk-'
        return bool(self.api_key) and bool(self.model)
    
    async def init(self):
        if not self.api_key:
            logger.warning("OPENAI_API_KEY is missing. Operating in mock mode.")

        base_url = self.base_url
        if base_url and base_url.endswith("/"):
            base_url = base_url[:-1]

        import httpx
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=base_url if base_url else None,
            timeout=httpx.Timeout(120.0, connect=60.0)
        )

    async def generate(self, prompt: str, session_id: Optional[str] = None, max_tokens: Optional[int] = None) -> str:
        if not self.client:
            raise RuntimeError("OpenAILLM is not initialized.")

        # Handle Memory
        memory = None
        current_messages = []
        
        try:
            memory = container.get("memory")
        except KeyError:
            pass

        if session_id and memory:
            # 1. Retrieve history
            history_context = await memory.get_context(session_id)
            # 2. Retrieve semantic context
            semantic_context = await memory.search_memory(session_id, prompt)
            
            system_prompt = "You are a helpful AI assistant."
            if semantic_context:
                system_prompt += f"\n\nContext from previous conversations:\n{semantic_context}"
            
            current_messages.append({"role": "system", "content": system_prompt})
            
            # Add history (simple append for now)
            history = await memory.history.get(session_id)
            for item in history:
                current_messages.append(item["content"])
        else:
            current_messages.append({"role": "user", "content": prompt})

        # Mock mode
        if not self.api_key:
            return f"[Mock OpenAI Response (No API Key) to: {prompt}]"

        if not self.model:
            raise RuntimeError("OpenAILLM model is not configured.")

        span_id = tracer.start_span("OpenAILLM.generate", {"model": self.model})
        try:
            # Final user message if using memory
            if session_id and memory:
                current_messages.append({"role": "user", "content": prompt})

            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=current_messages,
                max_tokens=max_tokens or config.SECURITY_MAX_OUTPUT_LENGTH
            )

            # Safe extraction
            if not resp or not resp.choices:
                tracer.end_span(span_id, status="error", error="Empty response from OpenAI")
                raise RuntimeError("Empty response from OpenAI API.")

            usage = {
                "prompt_tokens": resp.usage.prompt_tokens,
                "completion_tokens": resp.usage.completion_tokens,
                "total_tokens": resp.usage.total_tokens
            }
            
            message = resp.choices[0].message
            content = message.content.strip() if message and message.content else ""
            
            tracer.end_span(span_id, status="success", usage=usage)
            
            # Store interaction in memory
            if session_id and memory:
                await memory.add_interaction(session_id, prompt, content)
                
            return content

        except Exception as e:
            tracer.end_span(span_id, status="error", error=str(e))
            raise RuntimeError(f"OpenAILLM API call failed: {e}")
