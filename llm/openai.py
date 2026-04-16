from IRYM_sdk.llm.base import BaseLLM
from IRYM_sdk.core.config import config
from openai import AsyncOpenAI


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

        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )

            # Safe extraction
            if not resp or not resp.choices:
                raise RuntimeError("Empty response from OpenAI API.")

            message = resp.choices[0].message
            return message.content.strip() if message and message.content else ""

        except Exception as e:
            raise RuntimeError(f"OpenAILLM API call failed: {e}")