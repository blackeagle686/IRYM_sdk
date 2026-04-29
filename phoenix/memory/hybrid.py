from phoenix.memory.short_term import ShortTermMemory
from phoenix.memory.long_term import LongTermMemory
from phoenix.memory.session import SessionMemory
from phoenix.memory.reflection import ReflectionMemory

class HybridMemory:
    """
    Agent-specific memory manager that combines Short-Term, Long-Term, Session, and Reflection memories.
    """
    def __init__(self, semantic_memory_instance=None):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(semantic_memory_instance)
        self.session = SessionMemory()
        self.reflection = ReflectionMemory()

    async def add_interaction(self, session_id: str, role: str, content: str, metadata: Optional[dict] = None):
        self.short_term.add(role, content)
        await self.long_term.add(session_id, f"{role.capitalize()}: {content}")

    async def clear_session(self, session_id: str):
        """Clears all memory layers for a specific session."""
        self.short_term.clear()
        self.session.clear()
        self.reflection.clear()
        await self.long_term.semantic.clear(session_id)

    async def consolidate_reflections(self, llm):
        """Triggers consolidation of lessons learned."""
        await self.reflection.consolidate(llm)

    async def get_full_context(self, session_id: str, query: str = "") -> str:
        """Assembles context from all memory layers."""
        context_parts = []
        
        # 1. Reflections (Lessons Learned)
        reflections = self.reflection.get_reflections()
        if reflections:
            context_parts.append(reflections)
            
        # 2. Session Variables
        session_vars = self.session.get_all()
        if session_vars:
            context_parts.append(f"Session Variables:\n{session_vars}")
            
        # 3. Long Term Memory (if query provided)
        if query:
            ltm_results = await self.long_term.search(session_id, query)
            if ltm_results:
                context_parts.append(f"Relevant Past Knowledge:\n{ltm_results}")
                
        # 4. Short Term Memory
        stm_context = self.short_term.get_context()
        if stm_context:
            context_parts.append(f"Recent Conversation:\n{stm_context}")
            
        return "\n\n".join(context_parts)
