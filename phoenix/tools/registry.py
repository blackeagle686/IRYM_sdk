from typing import Dict, List, Type
from phoenix.tools.base import BaseTool
from phoenix.tools.search import WebSearchTool
from phoenix.tools.code import CodeExecutionTool
from phoenix.tools.io import FileReadTool, FileWriteTool, FileSearchTool

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found in registry")
        return self.tools[name]
        
    def get_all_tools_info(self) -> List[Dict]:
        return [t.to_dict() for t in self.tools.values()]

    @classmethod
    def load_default(cls) -> "ToolRegistry":
        registry = cls()
        registry.register(WebSearchTool())
        registry.register(CodeExecutionTool())
        registry.register(FileReadTool())
        registry.register(FileWriteTool())
        registry.register(FileSearchTool())
        return registry
