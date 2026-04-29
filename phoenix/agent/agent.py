import uuid
from phoenix.llm.openai import OpenAILLM
from phoenix.memory.hybrid import HybridMemory
from phoenix.tools.registry import ToolRegistry
from phoenix.cognition.thinker import Thinker
from phoenix.cognition.planner import Planner
from phoenix.cognition.reflector import Reflector
from phoenix.cognition.analyzer import Analyzer
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
        self.analyzer = Analyzer(self.llm)
        
        self.loop = AgentLoop(
            thinker=self.thinker,
            planner=self.planner,
            actor=self.actor,
            reflector=self.reflector,
            analyzer=self.analyzer
        )

    def register_tool(self, tool):
        """Helper to register a new tool to the agent's ToolRegistry."""
        self.tools.register(tool)

    async def run(self, prompt: str, session_id: str = None, max_iterations: int = 15, mode: str = "auto") -> str:
        """
        Run the agent with the given prompt.
        mode can be "auto", "plan", or "fast_ans".
        """
        # Auto-initialize LLM if it's our OpenAILLM and hasn't been initialized
        if hasattr(self.llm, "client") and self.llm.client is None:
            if hasattr(self.llm, "init"):
                await self.llm.init()

        if session_id is None:
            session_id = str(uuid.uuid4())
            
        # Add user prompt to memory
        await self.memory.add_interaction(session_id, "user", prompt)
        
        # Decide mode if auto
        actual_mode = mode
        if mode == "auto":
            classification_prompt = (
                f"Analyze the following user prompt and decide if it requires using tools and multi-step planning (like writing files, searching the web, or complex logic), "
                f"or if it is a simple question that can be answered immediately.\n\n"
                f"Prompt: {prompt}\n\n"
                f"Respond with exactly one word: 'PLAN' or 'FAST'."
            )
            classification = await self.llm.generate(classification_prompt, session_id=None)
            if "PLAN" in classification.upper():
                actual_mode = "plan"
            else:
                actual_mode = "fast_ans"
                
        if actual_mode == "fast_ans":
            # Fast answer mode: bypass the agent loop and just use the LLM directly with memory context
            context = await self.memory.get_full_context(session_id, query=prompt)
            fast_prompt = f"Context:\n{context}\n\nUser: {prompt}\nAnswer directly:"
            fast_answer = await self.llm.generate(fast_prompt, session_id=None)
            await self.memory.add_interaction(session_id, "assistant", fast_answer)
            return fast_answer
        else:
            # Start execution loop
            return await self.loop.run(prompt, self.memory, session_id, max_iterations=max_iterations)
