from typing import Optional
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
        if metadata:
            for key, value in metadata.items():
                self.session.set(key, value)

    async def add_context_item(self, session_id: str, key: str, value, source: str = "user"):
        """
        Interactive context API: store structured session context that can be
        reused by planner/thinker and surfaced in context bundles.
        """
        self.session.set(key, value)
        await self.long_term.add(session_id, f"Context[{source}] {key}: {value}")

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
        """Assembles context from all memory layers in parallel for speed."""
        import asyncio
        
        # Define async tasks for parallel execution
        tasks = []
        
        # 1. Reflections (Lessons Learned)
        tasks.append(asyncio.to_thread(self.reflection.get_reflections))
            
        # 2. Session Variables
        tasks.append(asyncio.to_thread(self.session.get_all))
            
        # 3. Long Term Memory (if query provided)
        if query:
            tasks.append(self.long_term.search(session_id, query))
        else:
            tasks.append(asyncio.sleep(0, result="")) # Dummy task
                
        # 4. Short Term Memory
        tasks.append(asyncio.to_thread(self.short_term.get_context))
        
        # Run all retrieval tasks concurrently
        results = await asyncio.gather(*tasks)
        
        reflections = results[0]
        session_vars = results[1]
        ltm_results = results[2]
        stm_context = results[3]
        
        context_parts = []
        if reflections:
            context_parts.append(reflections)
        if session_vars:
            context_parts.append(f"Session Variables:\n{session_vars}")
        if ltm_results:
            context_parts.append(f"Relevant Past Knowledge:\n{ltm_results}")
        if stm_context:
            context_parts.append(f"Recent Conversation:\n{stm_context}")
            
        return "\n\n".join(context_parts)

    async def get_context_bundle(self, session_id: str, query: str = "") -> dict:
        """
        Returns an interactive structured context bundle for advanced UIs/custom loops.
        """
        full_text = await self.get_full_context(session_id, query=query)
        return {
            "session_id": session_id,
            "query": query,
            "session_variables": self.session.get_all(),
            "reflections": self.reflection.get_reflections(),
            "recent_conversation": self.short_term.get_context(),
            "full_text": full_text,
        }



"""
    short term
    Advanced MEMORY Structure
    
    {
        "thinker": {
            "main_objective": "main objective related to this memory entry",
            "sub_objectives": ["sub objective 1", "sub objective 2"],
            "context_memory": [relevant memory entries to this sub objective],
            "summary_answer": "summary of what was done in this memory entry",
            "files":{
                "file_name": {
                    "file_path": "path/to/file",
                    "task": "edit/append/create",
                },  
            }, 
            "tasks": {
                "task_name": {
                    "description": "What the task is about",
                    "dependencies": ["other_task_name"],
                    "tools_required": ["tool_name"],
                    "periority": "high/medium/low"
                }
            }
        },

        
    }
    

"""