import unittest
import os
from phoenix.tools.io import FileReadTool, FileWriteTool, FileSearchTool

class TestIOTools(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.test_file = "io_test.txt"
        self.content = "hello phoenix\nthis is a test file"
        with open(self.test_file, "w") as f:
            f.write(self.content)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    async def test_file_read(self):
        tool = FileReadTool()
        result = await tool.execute(file_path=self.test_file)
        self.assertTrue(result.success)
        self.assertEqual(result.output, self.content)

    async def test_file_write(self):
        tool = FileWriteTool()
        new_file = "new_io_test.txt"
        result = await tool.execute(file_path=new_file, content="new content")
        self.assertTrue(result.success)
        self.assertTrue(os.path.exists(new_file))
        os.remove(new_file)

    async def test_file_search(self):
        tool = FileSearchTool()
        result = await tool.execute(path=self.test_file, pattern="phoenix")
        self.assertTrue(result.success)
        self.assertIn("io_test.txt:1: hello phoenix", result.output)

if __name__ == "__main__":
    unittest.main()
