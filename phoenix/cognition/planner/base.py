from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator

class BasePlanner(ABC):
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools

    @abstractmethod
    async def plan(self, objective: str, previous_results: str = "") -> Dict[str, Any]:
        pass

    @abstractmethod
    async def stream_thinking(self, objective: str, previous_results: str = "") -> AsyncGenerator[str, None]:
        pass
