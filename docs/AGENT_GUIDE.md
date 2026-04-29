# 🤖 Phoenix AI: Autonomous Agent Framework Guide

The Phoenix AI Agent Framework is a high-performance, modular system designed for building autonomous agents that can think, plan, and execute complex tasks. It moves beyond simple chat interfaces to create agents capable of engineering, research, and multi-step reasoning.

---

## 🧠 Cognitive Architecture

The Phoenix Agent operates on a "Cognitive Loop" inspired by human problem-solving patterns. Each step of the loop is handled by a specialized module:

1.  **Analyzer**: Concurrently scans the project structure, tech stack, and environment to provide the agent with "situational awareness."
2.  **Thinker**: Deconstructs the user prompt into core objectives and constraints.
3.  **Planner**: Generates a sequence of steps and selects the necessary tools to achieve the objectives.
4.  **Actor**: Executes the planned actions, potentially in parallel, using the Tool Manager.
5.  **Reflector**: Evaluates the outcome of actions, verifies results, and provides insights for the next iteration.

---

## 🚀 Getting Started

### 1. Basic Initialization

To use the agent, you need to initialize the Phoenix framework and then instantiate the `Agent` class.

```python
import asyncio
from phoenix import init_phoenix, startup_phoenix
from phoenix.agent import Agent

async def main():
    # 1. Initialize core services
    init_phoenix()
    await startup_phoenix()
    
    # 2. Create the agent (uses default OpenAI LLM and Hybrid Memory)
    agent = Agent()
    
    # 3. Run a task
    response = await agent.run("Create a summary of all files in the current directory.")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Execution Modes

The agent supports three execution modes via the `mode` parameter in `agent.run()`:

*   **`auto`** (Default): The agent decides if it can answer immediately or if it needs to enter a planning loop.
*   **`plan`**: Forces the agent into the full `Think -> Plan -> Act -> Reflect` loop. Best for complex tasks.
*   **`fast_ans`**: Bypasses the loop and provides a direct answer using available memory context. Best for simple questions.

```python
# Force planning for complex engineering
await agent.run("Refactor the memory module to support Redis.", mode="plan")

# Quick greeting
await agent.run("Who are you?", mode="fast_ans")
```

---

## 🛠️ Tool Integration

The agent's power comes from its tools. You can easily register custom tools using the `@tool` decorator.

```python
from phoenix.tools import tool

@tool(name="fetch_weather", description="Fetches the current weather for a city. Input: 'city' (str).")
def weather_tool(city: str):
    # Your custom logic here
    return f"The weather in {city} is sunny, 25°C."

# Register the tool to the agent
agent.register_tool(weather_tool)
```

---

## 🌐 Connecting to Applications

### 💻 CLI Integration (Interactive)

You can create a simple interactive CLI to chat with your agent.

```python
import asyncio
from phoenix import init_phoenix, startup_phoenix
from phoenix.agent import Agent

async def interactive_cli():
    init_phoenix()
    await startup_phoenix()
    agent = Agent()
    
    print("🐦‍🔥 Phoenix Agent CLI (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        # Run agent in auto mode
        response = await agent.run(user_input, mode="auto")
        print(f"\nPhoenix: {response}\n")

if __name__ == "__main__":
    asyncio.run(interactive_cli())
```

### ⚡ FastAPI Integration

FastAPI is ideal for asynchronous AI services. Use lifecycle hooks for clean initialization.

```python
from fastapi import FastAPI, Body
from phoenix import init_phoenix_full
from phoenix.agent import Agent
from contextlib import asynccontextmanager

# Global agent instance
agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    await init_phoenix_full()
    agent = Agent()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/agent/chat")
async def chat_with_agent(
    prompt: str = Body(..., embed=True),
    session_id: str = Body(None, embed=True)
):
    response = await agent.run(prompt, session_id=session_id)
    return {"answer": response, "session_id": session_id}
```

### 🎸 Django Integration

For Django, you can use `asyncio.run()` or build an `AsyncJsonWebsocketConsumer` for real-time streaming (recommended).

#### Simple View Example:
```python
# views.py
from django.http import JsonResponse
from phoenix.agent import Agent
from phoenix import init_phoenix, startup_phoenix
import asyncio

# Singleton agent for simplicity (or use a service manager)
_agent = None

async def get_agent():
    global _agent
    if _agent is None:
        init_phoenix()
        await startup_phoenix()
        _agent = Agent()
    return _agent

def agent_view(request):
    prompt = request.GET.get('q')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    agent = loop.run_until_complete(get_agent())
    response = loop.run_until_complete(agent.run(prompt))
    
    return JsonResponse({"reply": response})
```

---

## 🧠 Advanced: Hybrid Memory

The Agent uses `HybridMemory`, which manages:
*   **Short-Term**: Recent conversation turns.
*   **Long-Term**: Semantic retrieval from the Vector DB.
*   **Session**: Persistent state for the current objective.
*   **Reflection**: Insights and corrections learned during the loop.

This ensures the agent remains context-aware even during long, multi-step tasks.
