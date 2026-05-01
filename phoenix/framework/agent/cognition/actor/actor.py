import asyncio
from typing import Dict, Any
from .base import BaseActor

class Actor(BaseActor):
    """
    Executes plans by interacting with tools.
    Moved to cognition module for centralized agent logic.
    """
    
    async def execute(self, plan: Dict[str, Any]) -> str:
        actions = plan.get("actions", [])
        
        # Backward compatibility for single tool field
        if not actions and "tool" in plan:
            actions = [{"tool": plan["tool"], "kwargs": plan.get("kwargs", {})} ]
            
        if not actions:
            return "No actions specified in the plan."
            
        # Check for finish
        if any(a.get("tool") == "finish" for a in actions):
            return "Task marked as finished by Planner."
            
        # Execute all actions in parallel
        tasks = []
        for action in actions:
            tool_name = action.get("tool")
            kwargs = action.get("kwargs", {})
            tasks.append(self.tool_manager.execute_tool(tool_name, kwargs))
            
        results = await asyncio.gather(*tasks)
        
        # Combine results
        combined_results = []
        for i, res in enumerate(results):
            tool_name = actions[i].get("tool")
            combined_results.append(f"Result from {tool_name}: {res}")
            
        return "\n---\n".join(combined_results)
