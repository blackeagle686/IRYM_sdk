import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from phoenix.agent.loop import AgentLoop

class TestAgentLoop(unittest.IsolatedAsyncioTestCase):
    async def test_loop_run(self):
        # Mocking all dependencies
        thinker = MagicMock()
        thinker.analyze = AsyncMock(return_value="Objective")
        
        analyzer = MagicMock()
        analyzer.analyze_workspace = AsyncMock(return_value={"tech_stack": "Python"})
        
        planner = MagicMock()
        # First action then finish
        planner.plan = AsyncMock(side_effect=[
            {"actions": [{"tool": "tool1", "kwargs": {}}]},
            {"actions": [{"tool": "finish"}]}
        ])
        
        actor = MagicMock()
        actor.execute = AsyncMock(return_value="Action Success")
        
        reflector = MagicMock()
        reflector.reflect = AsyncMock(return_value={"is_complete": False, "reflection": "More to do"})
        # Update mock reflector to return complete on second call if needed, 
        # but Planner 'finish' will also break the loop.
        
        loop = AgentLoop(thinker, planner, actor, reflector, analyzer)
        
        memory = MagicMock()
        memory.session = MagicMock()
        memory.reflection = MagicMock()
        memory.add_interaction = AsyncMock()
        memory.consolidate_reflections = AsyncMock()

        result = await loop.run("test prompt", memory, "session_1", max_iterations=2)
        
        self.assertEqual(result, "Action Success")
        thinker.analyze.assert_called_once()
        analyzer.analyze_workspace.assert_called_once()
        self.assertEqual(planner.plan.call_count, 2)

if __name__ == "__main__":
    unittest.main()
