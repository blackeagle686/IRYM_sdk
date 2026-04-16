from IRYM_sdk.core.base import BaseService
from typing import Optional

class BaseLLM(BaseService):
    def is_available(self) -> bool:
        raise NotImplementedError

    async def generate(self, prompt: str, session_id: Optional[str] = None) -> str:
        raise NotImplementedError

class BaseVLM(BaseService):
    def is_available(self) -> bool:
        raise NotImplementedError

    async def generate_with_image(self, prompt: str, image_path: str, session_id: Optional[str] = None) -> str:
        raise NotImplementedError
