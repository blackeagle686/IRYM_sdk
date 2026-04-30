import asyncio
import json
from phoenix.agent.agent import Agent
from helpers import print_step

class IntegrationMockLLM:
    def __init__(self):
        self.call_count = 0

    async def init(self): pass

    async def generate(self, prompt: str, **kwargs) -> str:
        self.call_count += 1
        p_lower = prompt.lower()
        
        # 1. Mode classification
        if "decide if it requires using tools" in p_lower:
            return "PLAN"
            
        # 2. Thinker
        if "you are the 'thinker' module" in p_lower:
            return "OBJECTIVE: Create a hello world file. SUCCESS: file 'hello.txt' exists with content 'hello'."

        # 3. Analyzer
        if "you are the 'analyzer' module" in p_lower:
            return json.dumps({
                "relevant_files": [],
                "tech_stack": "Python",
                "summary": "Empty workspace"
            })

        # 4. Planner
        if "you are the 'planner' module" in p_lower:
            return json.dumps({
                "actions": [
                    {"tool": "write_file", "kwargs": {"path": "hello.txt", "content": "hello"}}
                ]
            })

        # 5. Reflector
        if "you are the 'reflector' module" in p_lower:
            return json.dumps({
                "is_complete": True,
                "reflection": "File created successfully."
            })

        return "Mocked response"

class MockToolRegistry:
    def get_all_tools_info(self): return {}
    async def execute(self, tool_name, kwargs):
        return f"Executed {tool_name} with {kwargs}"
    @classmethod
    def load_default(cls): return cls()

async def test_agent_integration():
    print_step("Initializing Agent with IntegrationMockLLM")
    llm = IntegrationMockLLM()
    
    # We'll use a custom tool manager to avoid real tool execution
    from phoenix.execution.tool_manager import ToolManager
    tools = MockToolRegistry()
    tool_manager = ToolManager(tools)
    
    agent = Agent(llm=llm, tools=tools, tool_manager=tool_manager)
    
    print_step("Running Agent with prompt: 'write hello to hello.txt'")
    result = await agent.run("write hello to hello.txt", session_id="test_session")
    
    print_step("Verifying final result")
    print(f"Final Answer: {result}")
    assert "Executed write_file" in result or "File created" in result or "Mocked response" in result
    
    print_step("Verifying memory persistence")
    context = await agent.memory.get_full_context("test_session")
    assert "hello.txt" in context or "Objective" in context
    
    print_step("Agent Integration Test passed")

if __name__ == "__main__":
    asyncio.run(test_agent_integration())
