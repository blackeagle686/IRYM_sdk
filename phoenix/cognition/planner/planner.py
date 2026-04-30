import json
import re
from typing import Dict, Any, AsyncGenerator
from .base import BasePlanner
from ..utils import parse_llm_json

class Planner(BasePlanner):
    """
    Generates actionable steps and selects tools based on the Thinker's objective.
    """
    
    def __init__(self, llm, tools):
        super().__init__(llm, tools)
        self._cached_tool_info = None

    def _build_planner_prompt(self, objective: str, previous_results: str = "") -> str:
        if self._cached_tool_info is None:
            self._cached_tool_info = json.dumps(self.tools.get_all_tools_info(), indent=2)

        available_tools = self._cached_tool_info

        system_prompt = f"""
        You are the 'Planner' module of an autonomous agent.
        Based on the given objective, formulate the next action using one of the available tools.
        If the objective is already met based on previous results, you can use a 'finish' tool.
        Rules:
        1. Actions Over Talking: never claim completion unless verifiable action results show objective is complete.
        2. Verify Completion: use 'finish' only after at least one concrete tool action, except for pure conversational asks.
        3. Precision Editing: prefer file_read -> file_edit loops for existing files.
        4. For new/large files, prefer chunked creation with file_append (imports -> structure -> implementation).
        
        Available Tools:
        {available_tools}
        
        Previous Results:
        {previous_results}
        
        You must respond with a JSON object strictly following this format:
        {{
            "actions": [
                {{"tool": "tool_name", "kwargs": {{"arg1": "value1"}}}},
                {{"tool": "tool_name", "kwargs": {{"arg1": "value1"}}}}
            ]
        }}
        If you believe the task is complete, use "tool": "finish".
        You can specify multiple independent actions if they can be performed simultaneously.
        """
        return f"{system_prompt}\n\nObjective: {objective}\n\nPlan (JSON only):"

    async def stream_thinking(self, objective: str, previous_results: str = "") -> AsyncGenerator[str, None]:
        thinking_prompt = f"""
        You are the Planner and must briefly explain your next-step reasoning before taking action.
        Objective: {objective}
        Previous results: {previous_results}

        Produce concise thought text describing:
        1) what you will do next
        2) why it is the best next action
        3) what success signal you expect
        """

        stream_fn = getattr(self.llm, "generate_stream", None)
        if callable(stream_fn):
            try:
                stream = stream_fn(thinking_prompt, session_id=None, max_tokens=200)
                if hasattr(stream, "__aiter__"):
                    yielded = False
                    async for chunk in stream:
                        if chunk:
                            yielded = True
                            yield str(chunk)
                    if yielded:
                        return
            except Exception:
                pass

        text = await self.llm.generate(thinking_prompt, session_id=None, max_tokens=200)
        if text:
            for token in text.split():
                yield token + " "

    async def plan(self, objective: str, previous_results: str = "") -> Dict[str, Any]:
        full_prompt = self._build_planner_prompt(objective, previous_results)
        response = await self.llm.generate(full_prompt, session_id=None)
        
        data = parse_llm_json(response)
        if not data:
            return {"tool": "finish", "kwargs": {"reason": "Failed to parse planner output"}}
        return data
