import unittest
import asyncio
import json
import os
import shutil
from unittest.mock import MagicMock, AsyncMock
from phoenix.agent import Agent
from phoenix.tools.base import ToolResult
from phoenix.memory.hybrid import HybridMemory

class FullAgentWorkflowTest(unittest.IsolatedAsyncioTestCase):
    """
    End-to-end integration test for the Phoenix AI Agent.
    Tests the complete cognitive cycle, memory tiers, and tool execution.
    """
    
    async def asyncSetUp(self):
        # Create a test directory for file tools
        self.test_dir = "./test_agent_workspace"
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Setup Mock LLM
        self.mock_llm = MagicMock()
        self.mock_llm.generate = AsyncMock()
        
        # Initialize Agent with Mock LLM but Real Memory and Tools
        self.memory = HybridMemory()
        self.agent = Agent(llm=self.mock_llm, memory=self.memory)

    async def asyncTearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    async def test_full_autonomous_refactor_workflow(self):
        print("\n" + "="*60)
        print("PHOENIX AI: FULL AGENT WORKFLOW INTEGRATION TEST")
        print("="*60)

        # --- STEP 1: DEFINE MOCK LLM RESPONSES ---
        
        # 1. Thinker Response (Analysis of objective)
        thinker_resp = "Core Intent: Create a file and verify it. Requirements: Use file tools. Success: File exists."
        
        # 2. Analyzer Response (Repo scan)
        analyzer_resp = json.dumps({
            "relevant_files": [],
            "tech_stack": "Python/Unittest",
            "summary": "This is a test environment."
        })
        
        # 3. Planner Response (First Iteration: Write file)
        planner_resp_1 = json.dumps({
            "actions": [
                {
                    "tool": "file_write",
                    "kwargs": {
                        "file_path": os.path.join(self.test_dir, "workflow_test.txt"),
                        "content": "Phoenix Agent Workflow Test"
                    }
                }
            ]
        })
        
        # 4. Reflector Response (First Iteration: Not complete)
        reflector_resp_1 = json.dumps({
            "is_complete": False,
            "reflection": "I have written the file, now I must verify it."
        })
        
        # 5. Planner Response (Second Iteration: Read file)
        planner_resp_2 = json.dumps({
            "actions": [
                {
                    "tool": "file_read",
                    "kwargs": {
                        "file_path": os.path.join(self.test_dir, "workflow_test.txt")
                    }
                }
            ]
        })
        
        # 6. Reflector Response (Second Iteration: Complete)
        reflector_resp_2 = json.dumps({
            "is_complete": True,
            "reflection": "The file was written and verified successfully. Objective complete."
        })

        # 7. Final response for 'finish'
        finish_resp = json.dumps({"actions": [{"tool": "finish"}]})

        # Setup prompt-aware side effect for parallel calls
        async def llm_side_effect(prompt, session_id=None):
            if "Thinker" in prompt:
                return thinker_resp
            if "Analyzer" in prompt:
                return analyzer_resp
            if "Reflector" in prompt:
                # Alternate between reflector responses
                if "written the file" not in self.memory.reflection.get_reflections():
                    return reflector_resp_1
                return reflector_resp_2
            if "Planner" in prompt:
                # 1. Check if we've already written the file by looking at the interaction history
                # We check for our specific success message from file_write
                history = self.memory.short_term.get_context()
                if "Successfully wrote to" not in history:
                    return planner_resp_1
                
                # 2. If file is written, check if we've already verified it (Reflector says complete)
                if "verified successfully" in self.memory.reflection.get_reflections():
                    return finish_resp
                
                # 3. Otherwise, proceed to read/verify
                return planner_resp_2
            return finish_resp

        self.mock_llm.generate.side_effect = llm_side_effect

        # --- STEP 2: RUN THE AGENT ---
        
        prompt = "Create a file named workflow_test.txt and write some content to it."
        print(f"\n[*] Starting Full Workflow with Prompt: '{prompt}'")
        
        result = await self.agent.run(prompt, mode="plan", max_iterations=3)
        
        # --- STEP 3: VERIFY OUTCOMES ---
        
        print("\n[v] Workflow Finished.")
        print(f"[*] Final Report Snippet: {result[:100]}...")

        # 1. Verify filesystem side effects
        file_path = os.path.join(self.test_dir, "workflow_test.txt")
        self.assertTrue(os.path.exists(file_path), "File should have been created by the Actor.")
        with open(file_path, "r") as f:
            self.assertEqual(f.read(), "Phoenix Agent Workflow Test")
        print("[v] Filesystem verification passed.")

        # 2. Verify Memory state
        reflections = self.memory.reflection.get_reflections()
        self.assertIn("verified successfully", reflections)
        print("[v] Reflection memory verification passed.")
        
        # 3. Verify Session state
        obj = self.memory.session.get("current_objective")
        self.assertEqual(obj, thinker_resp)
        print("[v] Session state verification passed.")

        print("\n" + "="*60)
        print("FULL WORKFLOW TEST COMPLETE: SUCCESS")
        print("="*60 + "\n")

if __name__ == "__main__":
    unittest.main()
