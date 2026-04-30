from phoenix.llm.base import BaseLLM
from phoenix.memory.hybrid import HybridMemory


"""
    Thinker must recongize all of the following from user prompt.
    semantic cache uset the main_objective to find relevant memory entries to pass back to thinker as context for better understanding of user prompt and workspace state.
    Thinker must return response like this: 
    { 
        "main_objective": "Refined main goal based on user prompt",
        "sub_objectives": [],
        "context_memory": [last_n relevant memory entries to the prompt],
        "summary_answer": "A concise summary of the user's request and the core objectives",
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
    }

"""

def generate_task(description: str, dependencies: list = None, tools_required: list = None, priority: str = "medium") -> dict:
    return {
        "description": description,
        "dependencies": dependencies or [],
        "tools_required": tools_required or [],
        "priority": priority
    }


class Thinker:
    """Analyzes user prompts, breaks them down, and understands core objectives."""
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    async def analyze(self, prompt: str, memory: HybridMemory, session_id: str) -> str:
        context = await memory.get_full_context(session_id, query=prompt)
        
        system_prompt = f"""
        You are the 'Thinker' module, the lead architect of an autonomous agent.
        Your job is to deconstruct complex user prompts into a refined, actionable objective.
        
        Guidelines:
        1. Identify the 'Core Intent' - what does the user actually want?
        2. Identify 'Implicit Requirements' - what else needs to happen for this to be correct?
        3. Define 'Success Criteria' - how will we know the task is done?
        
        Context from Memory:
        {context}
        """
        
        full_prompt = (
            f"{system_prompt}\n\n"
            f"User Request: {prompt}\n\n"
            "Respond with a comprehensive Objective Analysis (Core Intent + Requirements + Success Criteria):"
        )
        return await self.llm.generate(full_prompt, session_id=None, max_tokens=200)
