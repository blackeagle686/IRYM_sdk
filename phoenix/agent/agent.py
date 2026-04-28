import uuid
from phoenix.llm.openai import OpenAILLM
from phoenix.memory.hybrid import HybridMemory
from phoenix.tools.registry import ToolRegistry
from phoenix.cognition.thinker import Thinker
from phoenix.cognition.planner import Planner
from phoenix.cognition.reflector import Reflector
from phoenix.execution.actor import Actor
from phoenix.execution.tool_manager import ToolManager
from phoenix.agent.loop import AgentLoop

class Agent:
    """The main Agent class that integrates LLM, memory, tools, and cognition modules."""
    def __init__(self, llm=None, memory=None, tools=None):
        # Default LLM to OpenAILLM (using LongCat-Flash-Chat by default via its config fallback)
        self.llm = llm if llm is not None else OpenAILLM()
        self.memory = memory if memory is not None else HybridMemory()
        self.tools = tools if tools is not None else ToolRegistry.load_default()
        
        # Setup framework
        self.thinker = Thinker(self.llm)
        self.planner = Planner(self.llm, self.tools)
        self.tool_manager = ToolManager(self.tools)
        self.actor = Actor(self.tool_manager)
        self.reflector = Reflector(self.llm)
        
        self.loop = AgentLoop(
            thinker=self.thinker,
            planner=self.planner,
            actor=self.actor,
            reflector=self.reflector
        )

    async def run(self, prompt: str, session_id: str = None) -> str:
        # Auto-initialize LLM if it's our OpenAILLM and hasn't been initialized
        if hasattr(self.llm, "client") and self.llm.client is None:
            if hasattr(self.llm, "init"):
                await self.llm.init()

        if session_id is None:
            session_id = str(uuid.uuid4())
            
        # Add user prompt to memory
        await self.memory.add_interaction(session_id, "user", prompt)
        
        # Start execution loop
        return await self.loop.run(prompt, self.memory, session_id)
