from phoenix.tools.base import BaseTool, ToolResult
import os
from typing import List, Dict

class MultiBlockUpdateTool(BaseTool):
    """
    Tool for updating multiple non-contiguous blocks of code in a single file.
    """
    name = "file_update_multi"
    description = (
        "Updates multiple blocks of code in a file. "
        "Input: 'file_path' (str), 'edits' (list of dicts containing 'target' and 'replacement'). "
        "Each 'target' string must be unique and exist exactly in the file."
    )

    async def execute(self, file_path: str, edits: List[Dict[str, str]], **kwargs) -> ToolResult:
        try:
            if not os.path.exists(file_path):
                return ToolResult(success=False, output="", error=f"File not found: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content = content
            applied_count = 0
            
            for edit in edits:
                target = edit.get("target")
                replacement = edit.get("replacement")
                
                if not target:
                    continue
                    
                if target not in new_content:
                    return ToolResult(
                        success=False, 
                        output=f"Applied {applied_count} edits before failure.", 
                        error=f"Target content not found in file: {target[:50]}..."
                    )
                
                # Check for multiple occurrences to avoid ambiguity
                if new_content.count(target) > 1:
                    return ToolResult(
                        success=False, 
                        output=f"Applied {applied_count} edits before failure.", 
                        error=f"Target content is not unique in file (found {new_content.count(target)} occurrences): {target[:50]}..."
                    )

                new_content = new_content.replace(target, replacement)
                applied_count += 1

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return ToolResult(success=True, output=f"Successfully applied {applied_count} block updates to {file_path}")
            
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
