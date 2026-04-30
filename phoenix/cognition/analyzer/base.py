from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAnalyzer(ABC):
    def __init__(self, llm):
        self.llm = llm

    @abstractmethod
    async def analyze_workspace(self, prompt: str, root_dir: str = ".") -> Dict[str, Any]:
        pass
