import base64
import httpx
from IRYM_sdk.llm.base import BaseVLM
from IRYM_sdk.core.config import config

class LocalVLM(BaseVLM):
    def __init__(self):
        self.model = config.LOCAL_VLM_MODEL or "moondream"
        self.base_url = "http://localhost:11434/api/generate"

    def is_available(self) -> bool:
        # For simplicity, we assume if a model is set, it might be available.
        # A more robust check would involve the init check.
        return bool(self.model)

    async def init(self):
        # Check if ollama is running
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("http://localhost:11434/api/tags")
                if resp.status_code != 200:
                    print(f"Warning: Ollama not responding at {self.base_url}. LocalVLM might fail.")
        except Exception:
            print("Warning: Could not connect to local Ollama. Ensure Ollama is running for LocalVLM.")

    async def generate_with_image(self, prompt: str, image_path: str) -> str:
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [image_data],
                "stream": False
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                return response.json().get("response", "")
        except Exception as e:
            return f"Error in LocalVLM (Ollama): {str(e)}"
