from phoenix.execution.tool_manager import ToolManager

class Actor:
    """Executes plans by interacting with tools."""
    def __init__(self, tool_manager: ToolManager):
        self.tool_manager = tool_manager

    async def execute(self, plan: dict) -> str:
        import asyncio
        actions = plan.get("actions", [])
        
        # Backward compatibility for single tool field
        if not actions and "tool" in plan:
            actions = [{"tool": plan["tool"], "kwargs": plan.get("kwargs", {})}]
            
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
