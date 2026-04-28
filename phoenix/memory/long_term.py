from typing import List

class LongTermMemory:
    """Wraps semantic memory for factual recall in the agent framework."""
    def __init__(self, semantic_memory_instance=None):
        # Fallback to a mock list if no semantic memory instance is provided
        self.semantic = semantic_memory_instance
        self._mock_storage: List[str] = []

    async def add(self, session_id: str, content: str):
        if self.semantic:
            await self.semantic.add(session_id, content)
        else:
            self._mock_storage.append(content)

    async def search(self, session_id: str, query: str, limit: int = 3) -> str:
        if self.semantic:
            results = await self.semantic.search(session_id, query, limit=limit)
            if not results:
                return ""
            return "\n".join([str(r.get("text", r)) if isinstance(r, dict) else str(r) for r in results])
        else:
            # Very basic mock search
            results = [s for s in self._mock_storage if any(word in s for word in query.split())][:limit]
            return "\n".join(results)
