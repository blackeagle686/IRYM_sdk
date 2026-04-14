import chromadb
from typing import Any, List, Optional
from IRYM_sdk.vector.base import BaseVectorDB
from IRYM_sdk.core.config import config

class ChromaVectorDB(BaseVectorDB):
    def __init__(self, collection_name: str = "irym_collection"):
        self.persist_directory = config.CHROMA_PERSIST_DIR
        self.collection_name = collection_name
        self.client = None
        self.collection = None

    async def init(self):
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    async def search(self, query: str, limit: int = 5) -> List[Any]:
        if not self.collection:
            await self.init()
        
        results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )
        # Flatten results to a list of dicts or documents
        docs = []
        for i in range(len(results['documents'][0])):
            docs.append({
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                "id": results['ids'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            })
        return docs

    async def add(self, texts: List[str], metadatas: Optional[List[dict]] = None, ids: Optional[List[str]] = None) -> None:
        if not self.collection:
            await self.init()
        
        if not ids:
            import uuid
            ids = [str(uuid.uuid4()) for _ in texts]
        
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

    async def delete(self, ids: List[str]) -> None:
        if not self.collection:
            await self.init()
        self.collection.delete(ids=ids)

    async def clear(self) -> None:
        if not self.collection:
            await self.init()
        ids = self.collection.get()['ids']
        if ids:
            self.collection.delete(ids=ids)

    async def get_all(self) -> List[Any]:
        if not self.collection:
            await self.init()
        return self.collection.get()

    async def insert(self, vector: Any) -> None:
        # Placeholder for raw vector insertion if needed
        pass
