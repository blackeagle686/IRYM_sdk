from typing import List, Optional, Dict
from phoenix.memory.history import ConversationHistory
from phoenix.memory.semantic import SemanticMemory

class MemoryManager:
    """
    Unified manager for short-term and long-term memory.
    """
    def __init__(self, vector_db=None):
        self.history = ConversationHistory()
        self.semantic = SemanticMemory(vector_db)

    async def add_interaction(self, session_id: str, prompt: str, response: str, metadata: Optional[Dict] = None):
        """Adds a full interaction to both history and semantic memory."""
        # Add to short-term history
        await self.history.add(session_id, {"role": "user", "content": prompt}, metadata)
        await self.history.add(session_id, {"role": "assistant", "content": response}, metadata)
        
        # Add to long-term semantic memory
        await self.semantic.add(session_id, f"User: {prompt}\nAssistant: {response}", metadata)

    async def get_context(self, session_id: str, limit: int = 5) -> str:
        """Retrieves consolidated context for a given session."""
        history = await self.history.get(session_id, limit=limit)
        
        context_str = ""
        for item in history:
            role = item["content"].get("role", "unknown")
            content = item["content"].get("content", "")
            context_str += f"{role.capitalize()}: {content}\n"
            
        return context_str.strip()

    async def search_memory(self, session_id: str, query: str, limit: int = 3) -> str:
        """Searches semantic memory for relevant past facts."""
        results = await self.semantic.search(session_id, query, limit=limit)
        if not results:
            return ""
            
        context = "\nRelevant past information:\n"
        for res in results:
            if isinstance(res, dict):
                content = res.get("content", res.get("text", str(res)))
            else:
                content = str(res)
            context += f"- {content}\n"
        return context

    async def clear_session(self, session_id: str):
        """Clears both short-term and semantic memory for a session."""
        await self.history.clear(session_id)
        await self.semantic.clear(session_id)
