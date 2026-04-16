from typing import Any, List, Optional, Dict
from IRYM_sdk.memory.base import BaseMemory
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
        """Technically semantic memory doesn't just 'get' recent items in order, 
        but we can filter by session_id in the vector store."""
        if not self.vector_db:
            return []
            
        # This depends on vector_db supporting collection-level or metadata filtering
        # For now, we return empty or implement a search with empty query if supported.
        return []

    async def clear(self, session_id: str) -> None:
        # Vector DBs usually don't support deleting by metadata easily without collection support.
        # This might be tricky depending on the implementation in IRYM_sdk.vector.
        pass

    async def search(self, session_id: str, query: str, limit: int = 5) -> List[Any]:
        if not self.vector_db:
            return []
            
        # Search across all memory for this session
        results = await self.vector_db.search(query, limit=limit)
        # Filter by session_id if metadata filtering is available in the vector db
        # For now, we return all relevant hits.
        return results
