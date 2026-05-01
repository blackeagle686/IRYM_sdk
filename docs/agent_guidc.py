"""
Phoenix Agent Architecture & Usage Guide
========================================

1. Agent (phoenix.agent)
------------------------
The `Agent` class is the central orchestrator that brings together the LLM, Memory, Tools, and Cognition components. 
It operates an asynchronous `AgentLoop` that manages multi-step interactions. 
Key features:
- Dynamic component injection: You can override specific cognition parts (Thinker, Planner, etc.) or use the defaults.
- Multiple execution modes: `fast_ans` (direct LLM bypass), `plan` (multi-step execution loop), and `auto` (LLM decides which mode to use based on the prompt).
- Streaming capabilities: Output can be streamed progressively via `run_stream()`.

2. Memory (phoenix.memory)
--------------------------
Handles state and context retention over conversations.
- Short-Term Memory: Maintains the recent conversation history for immediate context.
- Semantic Memory: Interacts with a vector database to search for past facts and relevant long-term context.
- Hybrid Memory: Combines both, unifying access through the `InteractiveMemoryAdapter` or native `HybridMemory` implementations.

3. Cognition (phoenix.cognition)
--------------------------------
The 'Brain' of the agent is divided into distinct functional roles to allow specialized prompting and logic:
- Thinker: Analyzes the initial prompt to form main objectives and logical reasoning.
- Planner: Generates a sequence of actionable steps/tools to satisfy the objective.
- Actor: Interfaces with the ToolManager to physically execute the steps the Planner decided on.
- Reflector: Evaluates the output to ensure the goal was met or decides if re-planning is necessary.
- Analyzer: Dissects complex inputs and context for the rest of the cognition loop.

4. Tools (phoenix.tools)
------------------------
Tools are actionable capabilities the agent can invoke.
- `ToolRegistry`: A central repository for registering and retrieving tools.
- Default tools (`load_default()`) include `WebSearchTool`, `CodeExecutionTool`, and a suite of filesystem tools (`FileReadTool`, `FileWriteTool`, `MultiBlockUpdateTool`, etc.).
- Custom tools can be created by subclassing `BaseTool`.

========================================
FULL USAGE EXAMPLE
========================================
"""

import asyncio
import os
from phoenix.llm.openai import OpenAILLM
from phoenix.agent.agent import Agent
from phoenix.memory.hybrid import HybridMemory
from phoenix.tools.registry import ToolRegistry
from phoenix.tools.base import BaseTool

# ---------------------------------------------------------
# Custom Tool Example
# ---------------------------------------------------------
class GreetTool(BaseTool):
    """A custom tool that generates a greeting."""
    name = "greet_tool"
    description = "Generates a personalized greeting. Provide a 'name' parameter."
    
    def __init__(self):
        super().__init__()

    async def run(self, params: dict) -> str:
        name = params.get("name", "World")
        return f"Hello, {name}! I am the Phoenix Agent."

# ---------------------------------------------------------
# Agent Setup and Execution
# ---------------------------------------------------------
async def main():
    print("Initializing Phoenix Components...")
    
    # 1. Initialize LLM (uses LONG_CAT_FLASH_LITE or similar defaults via OpenAILLM)
    llm = OpenAILLM()
    
    # 2. Initialize Memory (HybridMemory manages both session history and semantic storage)
    memory = HybridMemory()
    
    # 3. Initialize Tools
    tools = ToolRegistry.load_default()
    # Register our custom tool
    tools.register(GreetTool())
    
    # 4. Create the Agent
    # The agent will automatically initialize Thinker, Planner, Actor, Reflector, Analyzer
    # using the provided LLM, Memory, and Tools.
    agent = Agent(
        llm=llm,
        memory=memory,
        tools=tools
    )
    
    # Optional: You can swap out a core component at runtime if you subclassed one
    # e.g., agent.set_component("thinker", MyCustomThinker(llm))

    print("\n--- Running Agent (Auto Mode) ---")
    session_id = "demo_session_001"
    
    # Example 1: A simple prompt that the Agent will likely classify as 'fast_ans'
    prompt_fast = "What is the capital of France?"
    print(f"\nUser: {prompt_fast}")
    
    # We can use run_stream to get chunked output
    print("Agent: ", end="", flush=True)
    async for chunk in agent.run_stream(prompt_fast, session_id=session_id, mode="auto"):
        if chunk["type"] == "chunk":
            print(chunk["content"], end="", flush=True)
    print("\n")

    # Example 2: A complex prompt requiring tools ('plan' mode)
    prompt_plan = "Please use the greet_tool to greet 'Alice' and then tell me what 2 + 2 is."
    print(f"\nUser: {prompt_plan}")
    
    # We can also use standard run()
    response = await agent.run(prompt_plan, session_id=session_id, mode="plan")
    print(f"Agent: {response}")

if __name__ == "__main__":
    # Note: Requires OPENAI_API_KEY to be set in environment or .env
    asyncio.run(main())
