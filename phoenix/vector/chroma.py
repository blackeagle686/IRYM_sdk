import chromadb
from typing import Any, List, Optional
from phoenix.vector.base import BaseVectorDB
from phoenix.core.config import config

class ChromaVectorDB(BaseVectorDB):
    def __init__(self, collection_name: str = "PhoenixAI_collection", embedding_service=None):
        self.persist_directory = config.CHROMA_PERSIST_DIR
        self.collection_name = collection_name
        self.embedding_service = embedding_service
        self.client = None
        self.collection = None

    async def init(self):
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Link our embedding service to Chroma's interface if provided
        embedding_function = None
        if self.embedding_service:
            from chromadb import EmbeddingFunction, Documents, Embeddings
            class SDKEmbeddingWrapper(EmbeddingFunction):
                def __init__(self, service):
                    self.service = service
                def __call__(self, input: Documents) -> Embeddings:
                    return self.service.embed_documents(input)
            
            embedding_function = SDKEmbeddingWrapper(self.embedding_service)

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=embedding_function
        )

    async def search(self, query: str, limit: int = 5, where: Optional[dict] = None) -> List[Any]:
        if not self.collection:
            await self.init()
        
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where=where
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

    async def get_by_metadata(self, where: dict) -> List[Any]:
        if not self.collection:
            await self.init()
        results = self.collection.get(where=where)
        docs = []
        for i in range(len(results['documents'])):
            docs.append({
                "content": results['documents'][i],
                "metadata": results['metadatas'][i] if results['metadatas'] else {},
                "id": results['ids'][i]
            })
        return docs

    async def insert(self, vector: Any) -> None:
        # Placeholder for raw vector insertion if needed
        pass
