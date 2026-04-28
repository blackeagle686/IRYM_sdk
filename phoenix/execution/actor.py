from phoenix.execution.tool_manager import ToolManager

class Actor:
    """Executes plans by interacting with tools."""
    def __init__(self, tool_manager: ToolManager):
        self.tool_manager = tool_manager

    async def execute(self, plan: dict) -> str:
        tool_name = plan.get("tool")
        kwargs = plan.get("kwargs", {})
        
        if not tool_name:
            return "No tool specified in the plan."
            
        if tool_name == "finish":
            return "Task marked as finished by Planner."
            
        return await self.tool_manager.execute_tool(tool_name, kwargs)
