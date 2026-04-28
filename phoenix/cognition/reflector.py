from phoenix.llm.base import BaseLLM

class Reflector:
    """Evaluates the outcome of actions and determines task completion or replanning."""
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    async def reflect(self, objective: str, action: dict, result: str) -> dict:
        system_prompt = """
        You are the 'Reflector' module of an autonomous agent.
        Your job is to evaluate the result of the last action taken towards achieving the objective.
        
        Determine:
        1. Is the objective fully accomplished?
        2. What should be learned or saved from this action?
        
        Respond strictly with JSON:
        {
            "is_complete": boolean,
            "reflection": "A short summary of what was learned or what needs to be done next."
        }
        """
        
        full_prompt = f"{system_prompt}\n\nObjective: {objective}\nAction Taken: {action}\nResult: {result}\n\nReflection (JSON only):"
        response = await self.llm.generate(full_prompt, session_id=None)
        
        import json
        import re
        try:
            match = re.search(r'```(?:json)?(.*?)```', response, re.DOTALL)
            if match:
                response = match.group(1)
            data = json.loads(response.strip())
            return {
                "is_complete": bool(data.get("is_complete", False)),
                "reflection": str(data.get("reflection", ""))
            }
        except json.JSONDecodeError:
            return {"is_complete": False, "reflection": "Failed to parse reflection"}
