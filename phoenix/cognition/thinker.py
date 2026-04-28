from phoenix.llm.base import BaseLLM
from phoenix.memory.hybrid import HybridMemory

class Thinker:
    """Analyzes user prompts, breaks them down, and understands core objectives."""
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    async def analyze(self, prompt: str, memory: HybridMemory, session_id: str) -> str:
        context = await memory.get_full_context(session_id, query=prompt)
        
        system_prompt = f"""
        You are the 'Thinker' module of an autonomous agent.
        Your job is to analyze the user's request and break it down into a clear objective.
        Do not solve the task, just define the core objective clearly.
        
        Context:
        {context}
        """
        
        full_prompt = f"{system_prompt}\n\nUser Request: {prompt}\n\nObjective:"
        return await self.llm.generate(full_prompt, session_id=None) # We pass None so it doesn't use the standard memory manager
