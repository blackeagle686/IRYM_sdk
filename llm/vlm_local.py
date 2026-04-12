from IRYM_sdk.llm.base import BaseVLM

class LocalVLM(BaseVLM):
    def __init__(self):
        self.model = None

    async def init(self):
        self.model = "MockLocalVLM"

    async def generate_with_image(self, prompt: str, image_path: str) -> str:
        if not self.model:
            raise RuntimeError("LocalVLM is not initialized.")
        return f"[Local VLM Output for prompt '{prompt}' and image '{image_path}']"
