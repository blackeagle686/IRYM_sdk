from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


# =========================
# Structured Response Models
# =========================

@dataclass
class FileTask:
    file_path: str
    operation: str  # create | edit | append


@dataclass
class Task:
    task_id: str
    description: str
    dependencies: List[str]
    tools_required: List[str]
    priority: str
    status: str = "pending"


@dataclass
class ThinkerOutput:
    main_objective: str
    sub_objectives: List[str]
    context_memory: List[str]
    summary_answer: str
    files: Dict[str, FileTask]
    tasks: Dict[str, Task]


# =========================
# Base Thinker
# =========================

class BaseThinker(ABC):
    def __init__(self, llm):
        self.llm = llm

    # -------------------------
    # Core Pipeline
    # -------------------------
    async def think(self, prompt: str) -> ThinkerOutput:
        """
        Full thinking pipeline (orchestrated)
        """

        main_objective = await self.generate_main_objective(prompt)
        sub_objectives = await self.generate_sub_objectives(main_objective)
        context_memory = await self.retrieve_context_memory(main_objective)
        summary = await self.summarize(prompt)

        return self._build_output(
            main_objective,
            sub_objectives,
            context_memory,
            summary
        )

    # -------------------------
    # Abstract Methods
    # -------------------------

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

    # -------------------------
    # Output Builders
    # -------------------------

    def _build_output(
        self,
        main_objective: str,
        sub_objectives: List[str],
        context_memory: List[str],
        summary: str
    ) -> ThinkerOutput:

        return ThinkerOutput(
            main_objective=main_objective,
            sub_objectives=sub_objectives,
            context_memory=context_memory,
            summary_answer=summary,
            files={},
            tasks={}
        )

    def generate_file_task(self, file_path: str, operation: str) -> FileTask:
        return FileTask(file_path=file_path, operation=operation)

    def generate_task(
        self,
        task_id: str,
        description: str,
        dependencies: Optional[List[str]] = None,
        tools_required: Optional[List[str]] = None,
        priority: str = "medium"
    ) -> Task:

        return Task(
            task_id=task_id,
            description=description,
            dependencies=dependencies or [],
            tools_required=tools_required or [],
            priority=priority,
            status="pending"
        )

    # -------------------------
    # LLM Prompt Builder
    # -------------------------

    def build_llm_input(
        self,
        prompt: str,
        context_memory: List[str]
    ) -> str:

        context_str = "\n".join(context_memory) if context_memory else "None"

        return f"""
You are an advanced AI Thinker.

User Prompt:
{prompt}

Relevant Context:
{context_str}

Tasks:
1. Extract main objective
2. Break into sub-objectives
3. Provide concise summary

Return JSON only.
"""

    # -------------------------
    # LLM Output Parser (Safe)
    # -------------------------

    def parse_llm_output(self, raw_output: str) -> Dict[str, Any]:
        """
        Safe parsing with fallback
        """
        import json

        try:
            return json.loads(raw_output)
        except Exception:
            return {
                "main_objective": "",
                "sub_objectives": [],
                "context_memory": [],
                "summary_answer": raw_output
            }