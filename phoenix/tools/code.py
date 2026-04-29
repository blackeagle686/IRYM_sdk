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

class PythonAnalyzerTool(BaseTool):
    """
    Fast AST-based analyzer for Python files to map classes and functions.
    """
    name = "python_analyzer"
    description = "Analyzes a Python file and returns an index of all classes and functions with their line numbers. Input: 'file_path' (str)."

    async def execute(self, file_path: str, **kwargs) -> ToolResult:
        import os
        try:
            if not os.path.exists(file_path):
                return ToolResult(success=False, output="", error=f"File not found: {file_path}")

            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source)
            index = {
                "classes": {},
                "functions": [],
                "imports": []
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        "line_start": node.lineno,
                        "line_end": getattr(node, "end_lineno", node.lineno),
                        "methods": []
                    }
                    for n in node.body:
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            class_info["methods"].append({
                                "name": n.name,
                                "line_start": n.lineno,
                                "line_end": getattr(n, "end_lineno", n.lineno)
                            })
                    index["classes"][node.name] = class_info
                
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Check if it's a top-level function (parent is Module)
                    # Note: ast.walk doesn't give parents easily, so we can use a more surgical approach if needed.
                    # For simplicity in this fast tool, we list all functions.
                    pass

            # Refined top-level search
            top_functions = []
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    top_functions.append({
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": getattr(node, "end_lineno", node.lineno)
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    index["imports"].append(ast.unparse(node))

            index["functions"] = top_functions

            import json
            return ToolResult(success=True, output=json.dumps(index, indent=2))

        except SyntaxError as e:
            return ToolResult(success=False, output="", error=f"Syntax error in Python file: {e}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
