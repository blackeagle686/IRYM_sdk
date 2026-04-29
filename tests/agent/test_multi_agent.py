import unittest
import asyncio
import json
from unittest.mock import MagicMock, AsyncMock
from phoenix.agent import Agent

class MultiAgentCollaborationTest(unittest.IsolatedAsyncioTestCase):
    """
    Tests the interaction between multiple Agent instances.
    Simulates a 'Manager' and 'Worker' agent collaboration.
    """
    
    async def test_multi_agent_collaboration(self):
        print("\n" + "="*60)
        print("PHOENIX AI: MULTI-AGENT COLLABORATION TEST")
        print("="*60)

        # 1. Setup two independent agents
        # Agent A: The Architect (Manager)
        # Agent B: The Coder (Worker)
        
        mock_llm_a = MagicMock()
        mock_llm_a.generate = AsyncMock()
        
        mock_llm_b = MagicMock()
        mock_llm_b.generate = AsyncMock()
        
        agent_architect = Agent(llm=mock_llm_a)
        agent_coder = Agent(llm=mock_llm_b)

        print("[*] Two independent agents initialized (Architect & Coder).")

        # --- SCENARIO: Architect provides a spec, Coder implements it ---

        # Architect's "Plan" to give to Coder
        architect_spec = "DESIGN SPEC: Create a Python function 'multiply(a, b)' that returns the product."
        
        # Coder's "Implementation"
        coder_output = "CODE: def multiply(a, b): return a * b"

        # Mock Architect (Thinker -> Planner -> Finish with Spec)
        mock_llm_a.generate.side_effect = [
            "Think: Need to provide a spec.",    # Think
            '{"tech_stack": "Python"}',           # Analyze
            json.dumps({"actions": [{"tool": "finish"}]}), # Plan (Finish immediately with result)
            '{"is_complete": true, "reflection": "Spec provided"}', # Reflect
            architect_spec # The actual response returned by agent.run
        ]

        # Mock Coder (Thinker -> Planner -> Finish with Code)
        mock_llm_b.generate.side_effect = [
            "Think: Need to implement the spec.", # Think
            '{"tech_stack": "Python"}',            # Analyze
            json.dumps({"actions": [{"tool": "finish"}]}), # Plan
            '{"is_complete": true, "reflection": "Code written"}', # Reflect
            coder_output # The actual response
        ]

        # --- EXECUTION ---

        print("\n[STEP 1] Architect is generating a specification...")
        spec = await agent_architect.run("Design a multiplication function.", mode="plan")
        print(f"[v] Architect Spec: {spec}")

        print("\n[STEP 2] Passing Spec to Coder for implementation...")
        code = await agent_coder.run(f"Implement this specification: {spec}", mode="plan")
        print(f"[v] Coder Output: {code}")

        # --- VERIFICATION ---
        
        self.assertIn("DESIGN SPEC", spec)
        self.assertIn("CODE", code)
        self.assertIn("multiply(a, b)", code)
        
        # Verify they have independent memories
        self.assertNotEqual(agent_architect.memory, agent_coder.memory)
        print("[v] Memory isolation verified.")

        print("\n" + "="*60)
        print("MULTI-AGENT COLLABORATION TEST COMPLETE: SUCCESS")
        print("="*60 + "\n")

if __name__ == "__main__":
    unittest.main()
