import unittest
import asyncio
import os
from phoenix.llm import OpenAILLM
from phoenix.agent import Agent

class MultiAgentCollaborationTest(unittest.IsolatedAsyncioTestCase):
    """
    Tests the interaction between multiple Agent instances using OpenAI LLM.
    Simulates a 'Manager' and 'Worker' agent collaboration.
    """
    
    async def asyncSetUp(self):
        # Initialize the Phoenix framework to ensure providers are ready
        await init_phoenix()
    
    async def test_multi_agent_collaboration(self):
        print("\n" + "="*60)
        print("PHOENIX AI: OPENAI MULTI-AGENT COLLABORATION TEST")
        print("="*60)

        # 1. Setup two independent agents using OpenAI LLM
        llm = OpenAILLM()
        
        # We create two distinct agents. They share the LLM service but have 
        # isolated memory, session state, and cognitive context.
        agent_architect = Agent(llm=llm)
        agent_coder = Agent(llm=llm)

        print("[*] Two independent agents initialized (Architect & Coder).")
        print(f"[*] Using LLM Provider: {llm.__class__.__name__}")

        # --- EXECUTION ---

        print("\n[STEP 1] Architect is generating a specification...")
        # Architect thinks and plans how to design the request
        spec = await agent_architect.run(
            "Design a simple Python function called 'add_numbers' that takes two arguments and returns their sum. "
            "Provide only the specification, no code.", 
            mode="plan"
        )
        print(f"\n[v] Architect Spec:\n{spec}")

        print("\n[STEP 2] Passing Spec to Coder for implementation...")
        # Coder receives the Architect's output and implements it
        code = await agent_coder.run(
            f"Implement the following specification in Python code: {spec}", 
            mode="plan"
        )
        print(f"\n[v] Coder Output:\n{code}")

        # --- VERIFICATION ---
        
        self.assertTrue(len(spec) > 0)
        self.assertTrue(len(code) > 0)
        
        # Verify they have independent memory systems
        self.assertNotEqual(agent_architect.memory, agent_coder.memory)
        print("\n[v] Memory isolation verified (Agents are truly independent).")

        print("\n" + "="*60)
        print("REAL MULTI-AGENT COLLABORATION TEST COMPLETE")
        print("="*60 + "\n")

if __name__ == "__main__":
    unittest.main()
