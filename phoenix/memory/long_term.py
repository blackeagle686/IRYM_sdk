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

    async def clear(self, session_id: str):
        if self.semantic:
            await self.semantic.clear(session_id)
        else:
            self._mock_storage.clear()

    async def search(self, session_id: str, query: str, limit: int = 3) -> str:
        if self.semantic:
            results = await self.semantic.search(session_id, query, limit=limit)
            if not results:
                return ""
            # Handle results being a list of dicts from Chroma
            formatted = []
            for r in results:
                if isinstance(r, dict):
                    formatted.append(r.get("content", r.get("text", str(r))))
                else:
                    formatted.append(str(r))
            return "\n".join(formatted)
        else:
            # Very basic mock search
            results = [s for s in self._mock_storage if any(word in s.lower() for word in query.lower().split())][:limit]
            return "\n".join(results)
