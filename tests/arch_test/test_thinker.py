import asyncio
from phoenix.cognition.thinker.thinker import Thinker
from phoenix.memory.hybrid.hybrid_manager import HybridMemoryManager
from tests.arch_test.helpers import print_step, MockLLM

async def test_thinker():
    print_step("Initializing Thinker with MockLLM")
    llm = MockLLM()
    thinker = Thinker(llm)
    memory = HybridMemoryManager()
    
    print_step("Running analysis on prompt")
    objective = await thinker.analyze("Build a todo app", memory, "session_1")
    
    print_step("Verifying objective response")
    assert objective == "Mocked response"
    
    print_step("Thinker validation passed")

if __name__ == "__main__":
    asyncio.run(test_thinker())
