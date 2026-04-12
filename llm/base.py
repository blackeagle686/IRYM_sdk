from IRYM_sdk.core.base import BaseService

class BaseLLM(BaseService):
    async def generate(self, prompt: str) -> str:
        raise NotImplementedError
