from IRYM_sdk.core.base import BaseService

class BaseLLM(BaseService):
    async def generate(self, prompt: str) -> str:
        raise NotImplementedError

class BaseVLM(BaseService):
    async def generate_with_image(self, prompt: str, image_path: str) -> str:
        raise NotImplementedError
