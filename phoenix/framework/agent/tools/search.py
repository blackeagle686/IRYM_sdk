from phoenix.framework.agent.tools.base import BaseTool, ToolResult
import json
import urllib.request
import urllib.parse

class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Searches the web for information using a search engine. Input should be a search query."

    async def execute(self, query: str, **kwargs) -> ToolResult:
        try:
            # We'll try to use duckduckgo html version or a public API for demonstration
            # In a real scenario, you'd use duckduckgo_search library or serpapi
            try:
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    results = [r for r in ddgs.text(query, max_results=3)]
                
                output = "\n".join([f"Title: {r['title']}\nSnippet: {r['body']}\nURL: {r['href']}" for r in results])
                if not output:
                    output = "No results found."
                return ToolResult(success=True, output=output)
            except ImportError:
                # Fallback simple mock if DDGS is not installed
                return ToolResult(
                    success=True, 
                    output=f"Mock search result for '{query}'.\n1. Example domain - Information about {query}."
                )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
