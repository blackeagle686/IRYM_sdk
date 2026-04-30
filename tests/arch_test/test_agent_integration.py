import asyncio
from phoenix.agent.agent import Agent
from helpers import print_step

async def test_agent_integration_real():
    print_step("Initializing Agent with Real Services")
    # By default, Agent() initializes with OpenAILLM and default ToolRegistry
    agent = Agent()
    
    # Initialize LLM if needed (handles API key loading etc)
    if hasattr(agent.llm, "init"):
        await agent.llm.init()
    
    print_step("Running Agent with prompt: 'say hello'")
    # Using a simple prompt to minimize API costs/tokens during test
    result = await agent.run("say hello", session_id="real_test_session", max_iterations=2)
    
    print_step("Verifying final result")
    print(f"Final Answer: {result}")
    assert len(result) > 0
    
    print_step("Verifying memory persistence in real memory layer")
    context = await agent.memory.get_full_context("real_test_session")
    print(f"Memory Context Sample: {context[:200]}...")
    assert len(context) > 0
    
    print_step("Agent Real Integration Test passed")

if __name__ == "__main__":
    asyncio.run(test_agent_integration_real())
