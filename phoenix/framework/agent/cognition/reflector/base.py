from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseReflector(ABC):
    def __init__(self, llm):
        self.llm = llm

    @abstractmethod
    async def reflect(self, objective: str, action: Dict[str, Any], result: str) -> Dict[str, Any]:
        pass
