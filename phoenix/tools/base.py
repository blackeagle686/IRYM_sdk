from typing import Any, Callable, Dict, Optional
from pydantic import BaseModel, Field

class ToolResult(BaseModel):
    success: bool
    output: Any
    error: Optional[str] = None

class BaseTool:
    name: str
    description: str
    
    async def execute(self, **kwargs) -> ToolResult:
        raise NotImplementedError("Tool must implement execute method")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description
        }
