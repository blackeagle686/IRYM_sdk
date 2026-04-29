import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from phoenix.memory.hybrid import HybridMemory
from phoenix.memory.reflection import ReflectionMemory
from phoenix.memory.session import SessionMemory

class TestMemorySystem(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.memory = HybridMemory()

    async def test_session_memory(self):
        self.memory.session.set("key", "value")
        self.assertEqual(self.memory.session.get("key"), "value")

    async def test_reflection_consolidation(self):
        mock_llm = MagicMock()
        mock_llm.generate = AsyncMock(return_value="Consolidated Insight")
        
        # Add 5 reflections to trigger consolidation threshold
        for i in range(5):
            self.memory.reflection.add_reflection(f"Lesson {i}")
            
        await self.memory.consolidate_reflections(mock_llm)
        
        reflections = self.memory.reflection.get_reflections()
        self.assertIn("Consolidated Insight", reflections)
        self.assertEqual(len(self.memory.reflection.reflections), 1)

    async def test_parallel_context_retrieval(self):
        # This test ensures the parallel retrieval logic doesn't crash
        context = await self.memory.get_full_context("session_1", query="test")
        self.assertIsInstance(context, str)

if __name__ == "__main__":
    unittest.main()
