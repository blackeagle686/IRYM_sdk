from typing import Any, List, Optional, Dict
from phoenix.memory.base import BaseMemory
# Using generic VectorDB from container
# We might need to handle cases where vector db is not initialized yet.

class SemanticMemory(BaseMemory):
    """
    Handles long-term retrieval using vector embeddings.
    """
    def __init__(self, vector_db=None):
        self.vector_db = vector_db

    async def add(self, session_id: str, data: Any, metadata: Optional[Dict] = None) -> None:
        if not self.vector_db:
            return
            
        metadata = metadata or {}
        metadata["session_id"] = session_id
        metadata["type"] = "memory_interaction"
        
        await self.vector_db.add(
            texts=[str(data)],
            metadatas=[metadata]
        )

    async def get(self, session_id: str, limit: int = 10) -> List[Any]:
        """Retrieve items filtered by session_id."""
        if not self.vector_db:
            return []
            
        results = await self.vector_db.get_by_metadata(where={"session_id": session_id})
        return results[:limit]

    async def clear(self, session_id: str) -> None:
        """Clear all memory entries for a specific session."""
        if not self.vector_db:
            return
            
        results = await self.vector_db.get_by_metadata(where={"session_id": session_id})
        ids = [res["id"] for res in results if isinstance(res, dict) and "id" in res]
        
        if ids:
            await self.vector_db.delete(ids=ids)

    async def search(self, session_id: str, query: str, limit: int = 5) -> List[Any]:
        """Search memory with session-specific filtering."""
        if not self.vector_db:
            return []
            
        # Filter by session_id
        results = await self.vector_db.search(query, limit=limit, where={"session_id": session_id})
        return results
