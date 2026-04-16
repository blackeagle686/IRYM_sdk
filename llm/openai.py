from IRYM_sdk.llm.base import BaseLLM
from IRYM_sdk.core.config import config
from openai import OpenAI

class OpenAILLM(BaseLLM):
    def __init__(self):
        self.api_key = config.OPENAI_API_KEY
        self.base_url = config.OPENAI_BASE_URL
        self.model = config.OPENAI_LLM_MODEL
        self.client = None

    def is_available(self) -> bool:
        return bool(self.api_key) and not self.api_key.startswith("ak_")

    async def init(self):
        if not self.api_key:
            print("Warning: OPENAI_API_KEY is missing. Operating in mock mode.")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    async def generate(self, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("OpenAILLM is not initialized.")
        if not self.api_key:
            return f"[Mock OpenAI Response (No API Key) to: {prompt}]"

        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return resp.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAILLM API call failed: {e}")
