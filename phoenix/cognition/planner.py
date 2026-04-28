from phoenix.llm.base import BaseLLM
from phoenix.tools.registry import ToolRegistry
import json
import re

class Planner:
    """Generates actionable steps and selects tools based on the Thinker's objective."""
    def __init__(self, llm: BaseLLM, tools: ToolRegistry):
        self.llm = llm
        self.tools = tools

    async def plan(self, objective: str, previous_results: str = "") -> dict:
        available_tools = json.dumps(self.tools.get_all_tools_info(), indent=2)
        
        system_prompt = f"""
        You are the 'Planner' module of an autonomous agent.
        Based on the given objective, formulate the next action using one of the available tools.
        If the objective is already met based on previous results, you can use a 'finish' tool.
        
        Available Tools:
        {available_tools}
        
        Previous Results:
        {previous_results}
        
        You must respond with a JSON object strictly following this format:
        {{
            "tool": "tool_name",
            "kwargs": {{"arg1": "value1"}}
        }}
        If you believe the task is complete, use "tool": "finish".
        """
        
        full_prompt = f"{system_prompt}\n\nObjective: {objective}\n\nPlan (JSON only):"
        response = await self.llm.generate(full_prompt, session_id=None)
        
        # Clean up JSON if LLM added markdown formatting
        try:
            # Extract json blocks if any
            match = re.search(r'```(?:json)?(.*?)```', response, re.DOTALL)
            if match:
                response = match.group(1)
            return json.loads(response.strip())
        except json.JSONDecodeError:
            # Fallback for bad JSON
            return {"tool": "finish", "kwargs": {"reason": "Failed to parse planner output"}}
