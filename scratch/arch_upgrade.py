"""
Phoenix Architecture 10/10 Migration Script
============================================
Applies all recommended improvements:
1. Split VLM out of services/llm/ -> services/vlm/
2. Rename framework/agent/agent/ -> framework/agent/core/
3. Rename services/insight/ -> services/retrieval/
4. Create contracts/, plugins/, middleware/ layers
5. Flesh out api/ structure
6. Add chatbot memory helpers
7. Rewrite all imports globally
"""

import os
import re
import shutil
import textwrap

ROOT = "/home/tlk/Documents/Projects/my_AItools/IRYM_sdk"
PHOENIX = os.path.join(ROOT, "phoenix")


def move_safe(src, dst):
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        print(f"  mv  {src.replace(ROOT,'.')}  ->  {dst.replace(ROOT,'.')}")
        shutil.move(src, dst)
    else:
        print(f"  SKIP (not found): {src.replace(ROOT,'.')}")


def mkdirs(*paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)
        init = os.path.join(p, "__init__.py")
        if not os.path.exists(init):
            with open(init, "w") as f:
                f.write("")


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(textwrap.dedent(content))
        print(f"  new {path.replace(ROOT, '.')}")


def rewrite_imports(replacements):
    for dirpath, _, filenames in os.walk(ROOT):
        if ".git" in dirpath or "__pycache__" in dirpath or "git_venv" in dirpath:
            continue
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                txt = open(fp, encoding="utf-8").read()
            except Exception:
                continue
            new = txt
            for pat, sub in replacements:
                new = re.sub(pat, sub, new)
            if new != txt:
                open(fp, "w", encoding="utf-8").write(new)
                print(f"  fix {fp.replace(ROOT,'.')}")


# ─────────────────────────────────────────────
# STEP 1: VLM -> services/vlm/
# ─────────────────────────────────────────────
print("\n[1] Splitting VLM out of services/llm/ → services/vlm/")
mkdirs(f"{PHOENIX}/services/vlm")
move_safe(f"{PHOENIX}/services/llm/vlm_local.py", f"{PHOENIX}/services/vlm/local.py")
move_safe(f"{PHOENIX}/services/llm/vlm_openai.py", f"{PHOENIX}/services/vlm/openai.py")
# Create vlm base
write_file(f"{PHOENIX}/services/vlm/base.py", """
    from abc import ABC, abstractmethod
    from typing import Optional

    class BaseVLM(ABC):
        \"\"\"Abstract base for all Vision-Language Model providers.\"\"\"

        @abstractmethod
        async def ask(self, prompt: str, image_path: str, **kwargs) -> str:
            pass

        @abstractmethod
        async def describe(self, image_path: str) -> str:
            pass
""")
# Update vlm __init__
with open(f"{PHOENIX}/services/vlm/__init__.py", "w") as f:
    f.write("from .local import LocalVLM\nfrom .openai import OpenAIVLM\n")


# ─────────────────────────────────────────────
# STEP 2: Rename agent/agent/ -> agent/core/
# ─────────────────────────────────────────────
print("\n[2] Renaming framework/agent/agent/ → framework/agent/core/")
move_safe(f"{PHOENIX}/framework/agent/agent", f"{PHOENIX}/framework/agent/core")


# ─────────────────────────────────────────────
# STEP 3: Rename services/insight/ -> services/retrieval/
# ─────────────────────────────────────────────
print("\n[3] Renaming services/insight/ → services/retrieval/")
move_safe(f"{PHOENIX}/services/insight", f"{PHOENIX}/services/retrieval")


# ─────────────────────────────────────────────
# STEP 4: Create phoenix/contracts/
# ─────────────────────────────────────────────
print("\n[4] Creating phoenix/contracts/ Protocol interfaces")
mkdirs(f"{PHOENIX}/contracts")

write_file(f"{PHOENIX}/contracts/llm.py", """
    from typing import Protocol, runtime_checkable, AsyncIterator

    @runtime_checkable
    class LLMProvider(Protocol):
        \"\"\"Protocol contract for all LLM providers.\"\"\"
        async def generate(self, prompt: str, **kwargs) -> str: ...
        async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]: ...
""")

write_file(f"{PHOENIX}/contracts/vlm.py", """
    from typing import Protocol, runtime_checkable

    @runtime_checkable
    class VLMProvider(Protocol):
        \"\"\"Protocol contract for all VLM providers.\"\"\"
        async def ask(self, prompt: str, image_path: str, **kwargs) -> str: ...
        async def describe(self, image_path: str) -> str: ...
""")

write_file(f"{PHOENIX}/contracts/vector.py", """
    from typing import Protocol, runtime_checkable, List, Optional, Any

    @runtime_checkable
    class VectorStore(Protocol):
        \"\"\"Protocol contract for all Vector DB adapters.\"\"\"
        async def add(self, texts: List[str], metadatas: Optional[List[dict]] = None) -> None: ...
        async def search(self, query: str, limit: int = 5) -> List[Any]: ...
        async def delete(self, ids: List[str]) -> None: ...
""")

write_file(f"{PHOENIX}/contracts/memory.py", """
    from typing import Protocol, runtime_checkable, Optional, Dict

    @runtime_checkable
    class MemoryBackend(Protocol):
        \"\"\"Protocol contract for memory backends.\"\"\"
        async def add_interaction(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None) -> None: ...
        async def get_context(self, session_id: str) -> str: ...
        async def clear_session(self, session_id: str) -> None: ...
""")

write_file(f"{PHOENIX}/contracts/tool.py", """
    from typing import Protocol, runtime_checkable, Any, Dict

    @runtime_checkable
    class ToolContract(Protocol):
        \"\"\"Protocol contract for agent tools.\"\"\"
        name: str
        description: str
        async def run(self, **kwargs: Any) -> Any: ...
        def schema(self) -> Dict: ...
""")

with open(f"{PHOENIX}/contracts/__init__.py", "w") as f:
    f.write(
        "from .llm import LLMProvider\n"
        "from .vlm import VLMProvider\n"
        "from .vector import VectorStore\n"
        "from .memory import MemoryBackend\n"
        "from .tool import ToolContract\n"
    )


# ─────────────────────────────────────────────
# STEP 5: Create phoenix/plugins/
# ─────────────────────────────────────────────
print("\n[5] Creating phoenix/plugins/ registry")
mkdirs(f"{PHOENIX}/plugins")

write_file(f"{PHOENIX}/plugins/registry.py", """
    from typing import Dict, Type, Any

    class PluginRegistry:
        \"\"\"
        Central registry for discovering and loading Phoenix plugins.
        Supports LLM providers, Vector DB adapters, Memory backends, and Tools.
        \"\"\"
        _plugins: Dict[str, Dict[str, Any]] = {
            \"llm\": {},
            \"vlm\": {},
            \"vector\": {},
            \"memory\": {},
            \"tool\": {},
        }

        @classmethod
        def register(cls, category: str, name: str, plugin_class: Type):
            \"\"\"Register a plugin class under a category with a given name.\"\"\"
            if category not in cls._plugins:
                cls._plugins[category] = {}
            cls._plugins[category][name] = plugin_class

        @classmethod
        def get(cls, category: str, name: str) -> Type:
            \"\"\"Retrieve a registered plugin class.\"\"\"
            try:
                return cls._plugins[category][name]
            except KeyError:
                raise ValueError(f\"Plugin '{name}' not found in category '{category}'.\")

        @classmethod
        def list_plugins(cls, category: str = None) -> dict:
            \"\"\"List all registered plugins or those in a specific category.\"\"\"
            if category:
                return list(cls._plugins.get(category, {}).keys())
            return {k: list(v.keys()) for k, v in cls._plugins.items()}

    registry = PluginRegistry()
""")

with open(f"{PHOENIX}/plugins/__init__.py", "w") as f:
    f.write("from .registry import PluginRegistry, registry\n")


# ─────────────────────────────────────────────
# STEP 6: Create phoenix/middleware/
# ─────────────────────────────────────────────
print("\n[6] Creating phoenix/middleware/ pipeline")
mkdirs(f"{PHOENIX}/middleware")

write_file(f"{PHOENIX}/middleware/base.py", """
    from abc import ABC, abstractmethod
    from typing import Any, Optional

    class BaseMiddleware(ABC):
        \"\"\"Abstract base class for all Phoenix middleware components.\"\"\"
        priority: int = 100  # Lower runs first

        @abstractmethod
        async def process_input(self, data: str, context: dict) -> str:
            \"\"\"Transform or validate incoming request data.\"\"\"
            return data

        @abstractmethod
        async def process_output(self, data: str, context: dict) -> str:
            \"\"\"Transform or filter outgoing response data.\"\"\"
            return data
""")

write_file(f"{PHOENIX}/middleware/pipeline.py", """
    from typing import List
    from .base import BaseMiddleware

    class MiddlewarePipeline:
        \"\"\"
        Executes a sorted chain of middleware for input/output processing.
        Middleware is sorted by priority (ascending = runs first).
        \"\"\"
        def __init__(self, middlewares: List[BaseMiddleware] = None):
            self._chain = sorted(middlewares or [], key=lambda m: m.priority)

        def add(self, middleware: BaseMiddleware):
            self._chain.append(middleware)
            self._chain.sort(key=lambda m: m.priority)

        async def run_input(self, data: str, context: dict = None) -> str:
            ctx = context or {}
            for m in self._chain:
                data = await m.process_input(data, ctx)
            return data

        async def run_output(self, data: str, context: dict = None) -> str:
            ctx = context or {}
            for m in reversed(self._chain):
                data = await m.process_output(data, ctx)
            return data
""")

write_file(f"{PHOENIX}/middleware/sanitizer.py", """
    import re
    from .base import BaseMiddleware

    class InputSanitizerMiddleware(BaseMiddleware):
        \"\"\"Strips dangerous patterns and normalizes whitespace from input.\"\"\"
        priority = 10

        async def process_input(self, data: str, context: dict) -> str:
            data = re.sub(r\"<[^>]+>\", \"\", data)  # Strip HTML tags
            data = \" \".join(data.split())          # Normalize whitespace
            return data

        async def process_output(self, data: str, context: dict) -> str:
            return data
""")

write_file(f"{PHOENIX}/middleware/rate_limiter.py", """
    import time
    from collections import defaultdict
    from .base import BaseMiddleware

    class RateLimiterMiddleware(BaseMiddleware):
        \"\"\"Simple in-memory per-session rate limiter.\"\"\"
        priority = 5

        def __init__(self, max_requests: int = 60, window_seconds: int = 60):
            self.max_requests = max_requests
            self.window = window_seconds
            self._counts = defaultdict(list)

        async def process_input(self, data: str, context: dict) -> str:
            session_id = context.get(\"session_id\", \"global\")
            now = time.time()
            self._counts[session_id] = [t for t in self._counts[session_id] if now - t < self.window]
            if len(self._counts[session_id]) >= self.max_requests:
                raise RuntimeError(f\"Rate limit exceeded for session '{session_id}'.\")
            self._counts[session_id].append(now)
            return data

        async def process_output(self, data: str, context: dict) -> str:
            return data
""")

with open(f"{PHOENIX}/middleware/__init__.py", "w") as f:
    f.write(
        "from .pipeline import MiddlewarePipeline\n"
        "from .base import BaseMiddleware\n"
        "from .sanitizer import InputSanitizerMiddleware\n"
        "from .rate_limiter import RateLimiterMiddleware\n"
    )


# ─────────────────────────────────────────────
# STEP 7: Flesh out api/ structure
# ─────────────────────────────────────────────
print("\n[7] Building out api/ structure")
mkdirs(
    f"{PHOENIX}/api/rest",
    f"{PHOENIX}/api/websocket",
    f"{PHOENIX}/api/adapters",
)

write_file(f"{PHOENIX}/api/rest/chatbot_router.py", """
    \"\"\"
    Ready-to-use FastAPI router for Phoenix ChatBot.
    Mount this in any FastAPI app with: app.include_router(chatbot_router)
    \"\"\"
    try:
        from fastapi import APIRouter, HTTPException
        from pydantic import BaseModel
    except ImportError:
        raise ImportError(\"Install fastapi and pydantic: pip install fastapi pydantic\")

    router = APIRouter(prefix=\"/chat\", tags=[\"ChatBot\"])

    class ChatRequest(BaseModel):
        session_id: str = \"default\"
        message: str

    class ChatResponse(BaseModel):
        session_id: str
        reply: str

    _bot_instance = None

    def init_router(bot_instance):
        \"\"\"Call this with your ChatBotInstance before mounting.\"\"\"
        global _bot_instance
        _bot_instance = bot_instance

    @router.post(\"/\", response_model=ChatResponse)
    async def chat(req: ChatRequest):
        if not _bot_instance:
            raise HTTPException(status_code=503, detail=\"ChatBot not initialized. Call init_router() first.\")
        _bot_instance.set_session(req.session_id)
        reply = await _bot_instance.chat(text=req.message)
        return ChatResponse(session_id=req.session_id, reply=reply)
""")

write_file(f"{PHOENIX}/api/rest/agent_router.py", """
    \"\"\"
    Ready-to-use FastAPI router for Phoenix Agent.
    \"\"\"
    try:
        from fastapi import APIRouter, HTTPException
        from pydantic import BaseModel
    except ImportError:
        raise ImportError(\"Install fastapi: pip install fastapi\")

    router = APIRouter(prefix=\"/agent\", tags=[\"Agent\"])

    class AgentRequest(BaseModel):
        session_id: str = \"default\"
        task: str

    class AgentResponse(BaseModel):
        session_id: str
        result: str

    _agent_instance = None

    def init_router(agent_instance):
        global _agent_instance
        _agent_instance = agent_instance

    @router.post(\"/run\", response_model=AgentResponse)
    async def run_agent(req: AgentRequest):
        if not _agent_instance:
            raise HTTPException(status_code=503, detail=\"Agent not initialized.\")
        result = await _agent_instance.run(req.task, session_id=req.session_id)
        return AgentResponse(session_id=req.session_id, result=str(result))
""")

write_file(f"{PHOENIX}/api/websocket/ws_handler.py", """
    \"\"\"
    WebSocket handler for streaming ChatBot responses.
    \"\"\"
    try:
        from fastapi import WebSocket, WebSocketDisconnect
    except ImportError:
        raise ImportError(\"Install fastapi: pip install fastapi\")

    _bot_instance = None

    def init_ws(bot_instance):
        global _bot_instance
        _bot_instance = bot_instance

    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_json()
                session_id = data.get(\"session_id\", \"default\")
                message = data.get(\"message\", \"\")
                if not _bot_instance:
                    await websocket.send_json({\"error\": \"Bot not initialized\"})
                    continue
                _bot_instance.set_session(session_id)
                reply = await _bot_instance.chat(text=message)
                await websocket.send_json({\"session_id\": session_id, \"reply\": reply})
        except WebSocketDisconnect:
            pass
""")

write_file(f"{PHOENIX}/api/adapters/fastapi_adapter.py", """
    \"\"\"
    FastAPI adapter: quickly mount Phoenix ChatBot and Agent into any FastAPI app.
    \"\"\"
    from phoenix.api.rest.chatbot_router import router as chatbot_router, init_router as init_chatbot
    from phoenix.api.rest.agent_router import router as agent_router, init_router as init_agent

    def mount_chatbot(app, bot_instance, prefix=\"\"):
        init_chatbot(bot_instance)
        app.include_router(chatbot_router, prefix=prefix)

    def mount_agent(app, agent_instance, prefix=\"\"):
        init_agent(agent_instance)
        app.include_router(agent_router, prefix=prefix)
""")

write_file(f"{PHOENIX}/api/adapters/django_adapter.py", """
    \"\"\"
    Django adapter: integrates Phoenix with Django views.
    \"\"\"
    import asyncio

    _bot_instance = None

    def init_django(bot_instance):
        global _bot_instance
        _bot_instance = bot_instance

    def phoenix_view(request):
        \"\"\"Django view that proxies requests to the Phoenix ChatBot.\"\"\"
        try:
            from django.http import JsonResponse
            from django.views.decorators.csrf import csrf_exempt
            import json
        except ImportError:
            raise ImportError(\"Django is not installed.\")

        if request.method == \"POST\":
            body = json.loads(request.body)
            message = body.get(\"message\", \"\")
            session_id = body.get(\"session_id\", \"default\")
            _bot_instance.set_session(session_id)
            loop = asyncio.new_event_loop()
            reply = loop.run_until_complete(_bot_instance.chat(text=message))
            loop.close()
            return JsonResponse({\"reply\": reply})
        return JsonResponse({\"error\": \"Only POST allowed\"}, status=405)
""")


# ─────────────────────────────────────────────
# STEP 8: Add Chatbot memory helpers
# ─────────────────────────────────────────────
print("\n[8] Adding chatbot/memory/context_window.py and summarizer.py")

write_file(f"{PHOENIX}/framework/chatbot/memory/context_window.py", """
    from typing import List, Dict

    class ContextWindow:
        \"\"\"
        Manages a sliding token/character window over conversation history.
        Ensures the active context never exceeds the LLM's token budget.
        \"\"\"
        def __init__(self, max_chars: int = 8000):
            self.max_chars = max_chars

        def trim(self, messages: List[Dict]) -> List[Dict]:
            \"\"\"
            Trims the oldest messages from the list until it fits within max_chars.
            Always preserves the system prompt (first message) if present.
            \"\"\"
            total = sum(len(m.get(\"content\", \"\")) for m in messages)
            system = [m for m in messages if m.get(\"role\") == \"system\"]
            rest = [m for m in messages if m.get(\"role\") != \"system\"]

            while total > self.max_chars and len(rest) > 1:
                removed = rest.pop(0)
                total -= len(removed.get(\"content\", \"\"))

            return system + rest
""")

write_file(f"{PHOENIX}/framework/chatbot/memory/summarizer.py", """
    from typing import List, Dict, Optional

    class ConversationSummarizer:
        \"\"\"
        Automatically condenses old conversation history using the LLM
        when the context window limit is approaching.
        \"\"\"
        def __init__(self, llm, threshold_chars: int = 6000):
            self.llm = llm
            self.threshold = threshold_chars

        async def maybe_summarize(self, messages: List[Dict]) -> List[Dict]:
            \"\"\"
            If total chars exceed threshold, summarize older messages into one block.
            Returns a compressed list of messages.
            \"\"\"
            total = sum(len(m.get(\"content\", \"\")) for m in messages)
            if total <= self.threshold:
                return messages

            system_msgs = [m for m in messages if m.get(\"role\") == \"system\"]
            convo_msgs = [m for m in messages if m.get(\"role\") != \"system\"]

            # Keep the last 4 messages intact, summarize the rest
            to_summarize = convo_msgs[:-4]
            to_keep = convo_msgs[-4:]

            if not to_summarize:
                return messages

            history_text = \"\\n\".join([f\"{m['role'].capitalize()}: {m['content']}\" for m in to_summarize])
            prompt = f\"Summarize this conversation concisely in 2-3 sentences:\\n{history_text}\"

            try:
                summary = await self.llm.generate(prompt)
                summary_msg = {\"role\": \"system\", \"content\": f\"[Earlier conversation summary]: {summary}\"}
                return system_msgs + [summary_msg] + to_keep
            except Exception:
                return messages  # Graceful fallback
""")


# ─────────────────────────────────────────────
# STEP 9: Rewrite all imports globally
# ─────────────────────────────────────────────
print("\n[9] Rewriting all broken imports globally...")
rewrite_imports([
    # VLM paths
    (r"phoenix\.services\.llm\.vlm_local", "phoenix.services.vlm.local"),
    (r"phoenix\.services\.llm\.vlm_openai", "phoenix.services.vlm.openai"),
    (r"from phoenix\.llm\.vlm_local", "from phoenix.services.vlm.local"),
    (r"from phoenix\.llm\.vlm_openai", "from phoenix.services.vlm.openai"),
    # agent/agent -> agent/core
    (r"phoenix\.framework\.agent\.agent\.", "phoenix.framework.agent.core."),
    (r"from phoenix\.framework\.agent\.agent import", "from phoenix.framework.agent.core import"),
    # insight -> retrieval
    (r"phoenix\.services\.insight\.", "phoenix.services.retrieval."),
    (r"from phoenix\.services\.insight import", "from phoenix.services.retrieval import"),
    (r"from phoenix\.insight\.", "from phoenix.services.retrieval."),
    (r"phoenix\.insight\.", "phoenix.services.retrieval."),
])

print("\n[Done] All steps completed!")
