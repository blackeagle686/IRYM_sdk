from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseThinker(ABC):
    def __init__(self, llm):
        self.llm = llm

    @abstractmethod
    async def think(self, prompt: str) -> Dict[str, Any]:
        """
        Main entry point: analyze prompt and return structured reasoning output
        """
        pass

    @abstractmethod
    async def generate_main_objective(self, prompt: str) -> str:
        pass

    @abstractmethod
    async def generate_sub_objectives(self, main_objective: str) -> List[str]:
        pass

    @abstractmethod
    async def retrieve_context_memory(self, main_objective: str) -> List[str]:
        pass

    @abstractmethod
    async def summarize(self, prompt: str) -> str:
        pass

    def generate_file_task(self, file_path: str, task: str) -> Dict[str, str]:
        return {
            "file_path": file_path,
            "task": task
        }
    
    def generate_llm_structured_output(self, main_objective: str, sub_objectives: List[str], context_memory: List[str], summary_answer: str) -> Dict[str, Any]:
        return {
            "main_objective": main_objective,
            "sub_objectives": sub_objectives,
            "context_memory": context_memory,
            "summary_answer": summary_answer,
            "files": {},  # Placeholder for file-related tasks
            "tasks": {}   # Placeholder for task-related details
        }
        
    def genereate_