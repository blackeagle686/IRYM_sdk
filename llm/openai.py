from IRYM_sdk.llm.base import BaseLLM
from IRYM_sdk.core.config import config
from openai import AsyncOpenAI
from IRYM_sdk.observability.tracing import tracer


class OpenAILLM(BaseLLM):
    def __init__(self):
        self.api_key = getattr(config, "OPENAI_API_KEY", None)
        self.base_url = getattr(config, "OPENAI_BASE_URL", None)
        self.model = getattr(config, "OPENAI_LLM_MODEL", None) or "gpt-4.1-mini"
        self.client = None

    def is_available(self) -> bool:
        return (
            bool(self.api_key)
            and not self.api_key.startswith("ak_")
            and bool(self.model)
        )

    async def init(self):
        if not self.api_key:
            print("Warning: OPENAI_API_KEY is missing. Operating in mock mode.")

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url if self.base_url else None,
        )

    async def generate(self, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("OpenAILLM is not initialized.")

        # Mock mode
        if not self.api_key:
            return f"[Mock OpenAI Response (No API Key) to: {prompt}]"

        if not self.model:
            raise RuntimeError("OpenAILLM model is not configured.")

        span_id = tracer.start_span("OpenAILLM.generate", {"model": self.model})
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
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
            return content

        except Exception as e:
            tracer.end_span(span_id, status="error", error=str(e))
            raise RuntimeError(f"OpenAILLM API call failed: {e}")