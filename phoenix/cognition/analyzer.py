import os
from typing import List, Dict
from phoenix.llm.base import BaseLLM

class Analyzer:
    """
    Scans the repository and identifies relevant files and architectural patterns 
    based on the user's prompt to assist the Planner.
    """
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    async def analyze_workspace(self, prompt: str, root_dir: str = ".") -> Dict:
        """
        Analyzes the root directory and identifies relevant files for the prompt.
        """
        # Get a list of files in the workspace (shallow)
        files = []
        for root, dirs, filenames in os.walk(root_dir):
            # Ignore common noise directories
            if any(p in root for p in [".git", "__pycache__", "venv", ".env", "node_modules"]):
                continue
            for f in filenames:
                files.append(os.path.join(root, f))
                if len(files) > 100: # Limit for speed
                    break
            if len(files) > 100:
                break

        files_str = "\n".join(files)
        
        system_prompt = """
        You are the 'Analyzer' module of an autonomous agent.
        Your job is to look at the list of files in the project and identify which ones are most relevant 
        to the user's request. Also, try to identify the tech stack or core architecture.
        
        Respond with exactly this JSON format:
        {
            "relevant_files": ["file1", "file2"],
            "tech_stack": "e.g. Python/FastAPI",
            "summary": "Brief architectural summary"
        }
        """
        
        full_prompt = f"{system_prompt}\n\nFiles in workspace:\n{files_str}\n\nUser Prompt: {prompt}\n\nAnalysis (JSON):"
        response = await self.llm.generate(full_prompt, session_id=None)
        
        import json
        import re
        try:
            match = re.search(r'```(?:json)?(.*?)```', response, re.DOTALL)
            if match:
                response = match.group(1)
            return json.loads(response.strip())
        except:
            return {
                "relevant_files": [],
                "tech_stack": "Unknown",
                "summary": "Failed to analyze workspace"
            }
