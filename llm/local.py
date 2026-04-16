import httpx
from IRYM_sdk.llm.base import BaseLLM
from IRYM_sdk.core.config import config

class LocalLLM(BaseLLM):
    def __init__(self):
        self.model = config.LOCAL_LLM_TEXT_MODEL or "llama3"
        self.base_url = "http://localhost:11434/api/generate"

    def is_available(self) -> bool:
        return bool(self.model)

    async def init(self):
        # Check if ollama is running
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("http://localhost:11434/api/tags")
                if resp.status_code != 200:
                    print(f"Warning: Ollama not responding at {self.base_url}")
        except Exception:
            print("Warning: Could not connect to local Ollama.")

    async def generate(self, prompt: str) -> str:
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                return response.json().get("response", "")
        except Exception as e:
            raise RuntimeError(f"LocalLLM (Ollama) call failed: {e}")
