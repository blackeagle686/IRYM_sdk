import asyncio
import os
import sys

# Add the project root to sys.path so we can import 'phoenix'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from phoenix.agent import Agent
from phoenix.llm.openai import OpenAILLM
from phoenix.memory.hybrid import HybridMemory
from phoenix.tools.registry import ToolRegistry

async def main():
    # 1. Initialize custom LLM (User asked to use OpenAILLM default key)
    # OpenAILLM uses LongCat-Flash-Chat and its default configuration when instantiated
    llm = OpenAILLM()
    
    # 2. Setup Hybrid Memory
    memory = HybridMemory()
    
    # 3. Load default tools (Web Search, Code Execution)
    tools = ToolRegistry.load_default()
    
    # 4. Instantiate Agent
    agent = Agent(llm=llm, memory=memory, tools=tools)
    
    print("Agent Initialized. Running task...")
    
    # 5. Run the Agent
    result = await agent.run("Analyze the latest news about Artificial Intelligence.")
    
    print("\n--- Final Output ---")
    print(result)
    
    print("\n--- Agent Reflections ---")
    print(memory.reflection.get_reflections())

if __name__ == "__main__":
    asyncio.run(main())
