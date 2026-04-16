from IRYM_sdk.core.base import BaseService

class BaseLLM(BaseService):
    def is_available(self) -> bool:
        raise NotImplementedError

    async def generate(self, prompt: str) -> str:
        raise NotImplementedError

class BaseVLM(BaseService):
    def is_available(self) -> bool:
        raise NotImplementedError

    async def generate_with_image(self, prompt: str, image_path: str) -> str:
        raise NotImplementedError
