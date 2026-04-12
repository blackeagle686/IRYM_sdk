from IRYM_sdk.core.base import BaseService
from typing import Any, List

class BaseVectorDB(BaseService):
    async def search(self, query: str) -> List[Any]:
        raise NotImplementedError

    async def insert(self, vector: Any) -> None:
        raise NotImplementedError
