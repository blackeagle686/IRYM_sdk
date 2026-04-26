from typing import Any, List, Optional, Dict
from phoenix.memory.base import BaseMemory
import time

class ConversationHistory(BaseMemory):
    """
    Handles short-term conversation history.
    """
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self._storage: Dict[str, List[Dict]] = {}

    async def add(self, session_id: str, data: Any, metadata: Optional[Dict] = None) -> None:
        if session_id not in self._storage:
            self._storage[session_id] = []
        
        entry = {
            "content": data,
            "metadata": metadata or {},
            "timestamp": time.time()
        }
        
        self._storage[session_id].append(entry)
        
        # Trim history
        if len(self._storage[session_id]) > self.max_history:
            self._storage[session_id] = self._storage[session_id][-self.max_history:]

    async def get(self, session_id: str, limit: int = 10) -> List[Dict]:
        history = self._storage.get(session_id, [])
        return history[-limit:]

    async def clear(self, session_id: str) -> None:
        if session_id in self._storage:
            self._storage[session_id] = []

    async def search(self, session_id: str, query: str, limit: int = 5) -> List[Dict]:
        """Simple keyword search in short-term history."""
        history = self._storage.get(session_id, [])
        results = [
            item for item in history 
            if query.lower() in str(item["content"]).lower()
        ]
        return results[-limit:]
