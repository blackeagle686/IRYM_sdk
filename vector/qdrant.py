from typing import Any, List
from IRYM_sdk.vector.base import BaseVectorDB
from IRYM_sdk.core.config import config

class QdrantVectorDB(BaseVectorDB):
    def __init__(self):
        self.url = config.QDRANT_URL
        self.client = None

    async def init(self):
        self.client = "MockQdrantClient"

    async def search(self, query: str) -> List[Any]:
        if not self.client:
            raise RuntimeError("QdrantVectorDB is not initialized.")
        return [f"Mock doc matching query: {query}"]

    async def insert(self, vector: Any) -> None:
        if not self.client:
            raise RuntimeError("QdrantVectorDB is not initialized.")
        pass
