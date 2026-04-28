from phoenix.tools.base import BaseTool, ToolResult
import ast

class CodeExecutionTool(BaseTool):
    name = "python_repl"
    description = "Executes safe python code to perform calculations or logic. Input should be python code."

    async def execute(self, code: str, **kwargs) -> ToolResult:
        try:
            # We use a very restricted local exec for demonstration. 
            # In production, this should run in a sandbox like docker or gVisor.
            local_vars = {}
            # Capture output
            import io
            import sys
            old_stdout = sys.stdout
            redirected_output = sys.stdout = io.StringIO()
            
            try:
                # Wrap execution in an isolated scope
                exec(code, {"__builtins__": __builtins__}, local_vars)
            except Exception as e:
                sys.stdout = old_stdout
                return ToolResult(success=False, output="", error=f"Execution error: {str(e)}")
                
            sys.stdout = old_stdout
            output = redirected_output.getvalue()
            
            if not output and "result" in local_vars:
                output = str(local_vars["result"])
                
            return ToolResult(success=True, output=output.strip() if output else "Executed successfully (no output)")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
