from typing import List, Optional, Dict, Any
from phoenix.framework.agent.memory.base.base_memory import BaseMemory
from .ltm_cell import LongMemoryCell
import uuid
import time

class LongTermMemoryManager(BaseMemory):
    """
    Manages long-term retrieval and storage using LongMemoryCell.
    """
    def __init__(self, semantic_memory_instance=None):
        self.semantic = semantic_memory_instance
        self._mock_storage: List[LongMemoryCell] = []

    async def add(self, session_id: str, data: Any, metadata: Optional[Dict] = None) -> None:
        content = str(data)
        
        # In a real implementation, we would generate embeddings here
        embedding = [] 
        
        cell = LongMemoryCell(
            memory_id=uuid.uuid4().hex,
            content=content,
            embedding=embedding,
            memory_type=metadata.get("type", "knowledge") if metadata else "knowledge",
            tags=metadata.get("tags", []) if metadata else [],
            source=metadata.get("source", "agent") if metadata else "agent",
            source_ref=session_id
        )

        if self.semantic:
            await self.semantic.add(session_id, content, metadata=metadata)
        else:
            self._mock_storage.append(cell)

    async def get(self, session_id: str, limit: int = 10) -> List[LongMemoryCell]:
        if self.semantic:
            # This would need adaptation if semantic returns raw dicts
            raw_results = await self.semantic.get(session_id, limit=limit)
            return raw_results 
        return self._mock_storage[-limit:]

    async def clear(self, session_id: str) -> None:
        if self.semantic:
            await self.semantic.clear(session_id)
        else:
            self._mock_storage.clear()

    async def search(self, session_id: str, query: str, limit: int = 5) -> List[LongMemoryCell]:
        if self.semantic:
            return await self.semantic.search(session_id, query, limit=limit)
        
        # Basic mock search
        results = [c for c in self._mock_storage if query.lower() in c.content.lower()]
        return results[:limit]
