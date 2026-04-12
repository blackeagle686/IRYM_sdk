from IRYM_sdk.llm.base import BaseLLM

class LocalLLM(BaseLLM):
    def __init__(self):
        self.model = None

    async def init(self):
        self.model = "MockLocalModel"

    async def generate(self, prompt: str) -> str:
        if not self.model:
            raise RuntimeError("LocalLLM is not initialized.")
        return f"[Local LLM Output for: {prompt}]"
