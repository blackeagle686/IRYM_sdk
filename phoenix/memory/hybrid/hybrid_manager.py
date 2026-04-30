from typing import Optional, Dict, Any, List
from ..short_term.stm_manager import ShortTermMemoryManager
from ..long_term.ltm_manager import LongTermMemoryManager
from ..semantic.semantic_search import SemanticSearch
from .hybrid_cell import HybridMemoryCell
import asyncio

class HybridMemoryManager:
    """
    Unified memory manager that combines Short-Term, Long-Term, and Semantic memories
    with advanced ranking.
    """
    def __init__(self, semantic_memory_instance=None):
        # In the new architecture, we compose managers
        self.short_term = ShortTermMemoryManager()
        self.long_term = LongTermMemoryManager(semantic_memory_instance)
        
        # We'll keep these for backward compatibility if they are still needed
        # but they should eventually be migrated to task_memory or persistence
        from ..session import SessionMemory
        from ..reflection import ReflectionMemory
        self.session = SessionMemory()
        self.reflection = ReflectionMemory()

    async def add_interaction(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        await self.short_term.add(session_id, {"role": role, "content": content}, metadata=metadata)
        await self.long_term.add(session_id, f"{role.capitalize()}: {content}", metadata=metadata)
        if metadata:
            for key, value in metadata.items():
                self.session.set(key, value)

    async def get_full_context(self, session_id: str, query: str = "") -> str:
        tasks = [
            asyncio.to_thread(self.reflection.get_reflections),
            asyncio.to_thread(self.session.get_all),
            self.short_term.get_context_string(session_id)
        ]
        
        if query:
            tasks.append(self.long_term.search(session_id, query))
        else:
            tasks.append(asyncio.sleep(0, result=[]))

        results = await asyncio.gather(*tasks)
        
        reflections = results[0]
        session_vars = results[1]
        stm_context = results[2]
        ltm_results = results[3]
        
        # Ranking logic could be applied here to ltm_results if they were HybridMemoryCells
        
        context_parts = []
        if reflections:
            context_parts.append(reflections)
        if session_vars:
            context_parts.append(f"Session Variables:\n{session_vars}")
        if ltm_results:
            # Format LTM results if they are cells
            ltm_text = "\n".join([str(r.content if hasattr(r, 'content') else r) for r in ltm_results])
            context_parts.append(f"Relevant Past Knowledge:\n{ltm_text}")
        if stm_context:
            context_parts.append(f"Recent Conversation:\n{stm_context}")
            
        return "\n\n".join(context_parts)

    def _rank_memories(self, cells: List[HybridMemoryCell]) -> List[HybridMemoryCell]:
        """
        Applies final ranking: final_score = 0.5*relevance + 0.3*importance + 0.2*recency
        """
        for cell in cells:
            cell.final_score = (
                0.5 * cell.relevance_score +
                0.3 * cell.importance_score +
                0.2 * cell.recency_score
            )
        return sorted(cells, key=lambda x: x.final_score, reverse=True)
