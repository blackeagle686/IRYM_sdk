# 🐦‍🔥 Phoenix AI (Advanced AI Infrastructure SDK)

<p align="center">
  <img src="./docs/statics/images/phx-light-circle.png" alt="Phoenix AI Logo" width="500">
</p>

A production-ready, modular backend infrastructure SDK designed for AI-powered Python backend services. 

Whether you are building with FastAPI, Django, or a custom event-driven service, **Phoenix AI** eliminates repetitive backend setup.

## 🏗️ Architecture Flow

The entire SDK is built around an **Everything is a Service** and **Interface-First** philosophy. Services are centrally managed by a Dependency Injection (DI) system, ensuring complete modularity and avoiding global state collision.

```mermaid
graph TD
    APP["Host Application (FastAPI/Django)"] -->|"Initializes"| INIT("Phoenix AI Initializer")
    APP -->|"Requests Service via get()"| DI{"DI Container"}
    INIT -->|"Registers Services"| DI
    
    subgraph Core
        DI
        CONF["Config & Settings"]
        LFC["Lifecycle Hooks"]
    end
    
    subgraph General Infrastructure
        DI -->|"Provides"| CACHE["Cache Service (RedisCache)"]
        DI -->|"Provides"| DB["DB Service (SQLAlchemyDB)"]
        DI -->|"Provides"| QUEUE["Queue Service (CeleryQueue)"]
    end

    subgraph Data Sources
        DS_GITHUB["GitHub Repos"]
        DS_WEB["Web Scraping"]
        DS_SQL["SQL Databases"]
        DS_API["External APIs"]
        DS_FILE["Local Files & Code"]
    end
    
    subgraph AI & Data Operations
        DI -->|"Provides"| LLM["LLM Service (OpenAI/Local)"]
        DI -->|"Provides"| VLM["VLM Service (OpenAI/Local)"]
        DI -->|"Provides"| AUDIO["Audio Service (STT/TTS)"]
        DI -->|"Provides"| VDB["Vector DB (QdrantVectorDB)"]
        DI -->|"Provides"| RAG["RAG Pipeline"]
        DI -->|"Provides"| INSIGHT["Insight Engine"]
        DI -->|"Provides"| MEMORY["Memory Service (History & Semantic)"]
        
        RAG -->|"Retrieves context from"| VDB
        RAG -->|"Generates answer via"| LLM
        RAG -.->|"Refines query via"| MEMORY
        
        LLM -->|"Enriched by"| MEMORY
        VLM -->|"Enriched by"| MEMORY
        MEMORY -->|"Stores/Retrieves semantic facts"| VDB
        
        INSIGHT -->|"Retrieves"| VDB
        INSIGHT -->|"Generates"| LLM
        INSIGHT -.->|"Caches"| CACHE
        
        DS_GITHUB --> RAG
        DS_WEB --> RAG
        DS_SQL --> RAG
        DS_API --> RAG
        DS_FILE --> RAG
    end
    
    subgraph Observability
        OBS["Logger & Tracer"] -.->|"Monitors"| CACHE
        OBS -.->|"Monitors"| DB
        OBS -.->|"Monitors"| LLM
        OBS -.->|"Monitors"| VLM
        OBS -.->|"Monitors"| AUDIO
        OBS -.->|"Monitors"| VDB
        OBS -.->|"Monitors"| MEMORY
    end
    
    subgraph Autonomous Agent
        AGENT["Agent Core & Loop"]
        COGNITION["Cognition (Thinker, Analyzer, Planner, Reflector)"]
        EXEC["Execution (Actor, ToolManager)"]
        TOOLS_REG["Tools (PythonAnalyzer, MultiBlockUpdate, etc.)"]
        HYBRID_MEM["Hybrid Memory (Parallel Retrieval)"]
        
        AGENT --> COGNITION
        AGENT --> EXEC
        AGENT --> HYBRID_MEM
        EXEC --> TOOLS_REG
        AGENT -.->|"Uses"| LLM
    end
```

## 🐦‍🔥 Key Requirements & Core Features

1. **Dependency Injection**: Central standard registry. No manual instantiation inside business logic.
2. **Interface First**: Every module complies with an asynchronous base contract (`BaseCache`, `BaseLLM`, `BaseVectorDB`, etc.).
3. **Flexible Vector DB**: Native support for **ChromaDB** (Default/Persistent) and **Qdrant**.
4. **Embedded Insights**: Pre-configured with `sentence-transformers` (`all-MiniLM-L6-v2`) for local embedding generation.
5. **RAG Orchestration**: All-in-one `RAGPipeline` that handles document loading (.pdf, .docx, .xlsx), SQL databases, external APIs, and web scraping.

## 📦 Installation
Choose the method that fits your workflow best.

### 1. Automated Installation (Recommended)
Get everything ready in one command (handles Python deps and Redis setup):
```bash
# For Linux/macOS/WSL
chmod +x install.sh
./install.sh

# For Windows
install.bat
```

### 2. Manual Installation
Alternatively, use the provided `Makefile` or `pip`:
```bash
# Full installation with all services (VDB, RAG, Memory, etc.)
make install-full

# Or basic installation
make install
```

### 3. Pip Installation (Official)
```bash
pip install phoenix-agent-ai

# Or with full local model support
pip install "phoenix-agent-ai[full]"
```
3. **Configure Environment Variables**:
   Copy the provided template and add your keys:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your settings:
   ```env
   OPENAI_API_KEY="your_key"
   REDIS_URL="redis://localhost:6379/0" 
   # See .env.example for more advanced options
   ```

### 🛠️ System Dependencies
- **Redis Server**: Required for stateful memory and caching.
  - Ubuntu: `sudo apt install redis-server`
  - macOS: `brew install redis`

## 🐦‍🔥 Framework Mode: High-Level ChatBot

The Phoenix AI SDK now includes a high-level **Framework Layer** that allows you to build complex AI agents with Vision, Speech, RAG, and Memory in just **one line of code**.

```python
from phoenix import ChatBot

# Build the complete AI Agent with Security and Custom Config
bot = (ChatBot(local=True, vlm=True)
       .with_rag(["./docs", "./src"])       # Folders or files
       .with_memory()                       # Enable session memory
       .with_security(mode="strict")        # Protection against Prompt Injection
       .with_system_prompt("Expert Dev")    # Guide bot behavior
       .build())

# Or switch to OpenAI with one line
# bot.with_openai(api_key="sk-...", base_url="https://api.openai.com")

# Multi-modal interaction
response = await bot.chat("What's in this image?", image_path="vision.jpg")
print(response) 
```
> [!TIP]
> Use `.set_session("user_123")` on the bot instance to switch between different users in production environments like FastAPI.

## 🐦‍🔥 Framework Mode: Autonomous Agent

The Phoenix AI SDK now supports creating a fully autonomous agent that can think, analyze, plan, execute tools, and reflect on its progress with a single line of code! 

> [!TIP]
> For a deep dive into the architecture and integration patterns, check out the **[Agent Framework Guide](./docs/AGENT_GUIDE.md)**, **[Django Integration Guide](./docs/DJANGO_INTEGRATION.md)**, **[GUI Integration Guide](./docs/GUI_INTEGRATION.md)**, or the **[API Integration Guide](./docs/API_INTEGRATION.md)**.

#### ⚡ High-Speed Cognitive Engine
*   **Parallel Awareness**: The `Thinker` and `Analyzer` run concurrently, allowing the agent to understand both your prompt and your project structure in a single cognitive step.
*   **Multi-Action Planning**: The agent can plan and execute multiple independent actions (tools) in parallel, cutting task completion time by up to 60%.
*   **Concurrent Memory**: Reflection, consolidation, and logging happen in the background, ensuring zero-latency transitions between agent steps.
*   **Hybrid Memory Layer**: Integrated `ShortTerm`, `LongTerm` (Vector), `Session`, and `Reflection` memories with parallel retrieval support.

```python
import asyncio
from phoenix.agent import Agent
from phoenix.llm.openai import OpenAILLM
from phoenix.memory.hybrid import HybridMemory
from phoenix.tools.registry import ToolRegistry

async def agent_demo():
    # Initialize the high-speed Agent
    agent = Agent() # Uses default OpenAILLM, HybridMemory, and Parallel Tools
    
    # Run a complex engineering task
    # The agent will automatically:
    # 1. Think: Deconstruct the prompt
    # 2. Analyze: Scan the repo structure and tech stack
    # 3. Plan: Create parallel steps for search and code analysis
    # 4. Act: Execute tools concurrently (e.g. searching while analyzing code)
    # 5. Reflect: Verify the fix and learn from the process
    
    prompt = "Find the redundant code in the memory module and optimize it using the new parallel patterns."
    result = await agent.run(prompt, mode="plan")
    
    print(f"Agent Engineering Report: {result}")
```

### 🐦‍🔥 Custom Tools & Engineering Suite

The Agent comes pre-configured with a suite of engineering-grade tools:
*   **`python_analyzer`**: (High-Speed) AST-based indexing of classes and functions for precise code navigation.
*   **`file_update_multi`**: (Atomic) Applies multiple code changes across different parts of a file in one go.
*   **`python_repl`**: Executes Python logic in a sandbox.
*   **`web_search`**: Live internet access for news and documentation.
*   **`file_read / file_write / file_search`**: Advanced filesystem operations.

You can also easily create and inject your own custom tools using the `@tool` decorator:

```python
from phoenix.tools import tool

# 1. Define your custom logic
@tool(name="custom_math", description="Calculates the square of a given number. Input: 'number' (int).")
def custom_math_tool(number: int):
    return f"The square of {number} is {number ** 2}"

# 2. Register it directly to the agent
agent.register_tool(custom_math_tool)

# 3. The agent can now autonomously use 'custom_math' in its planning!
await agent.run("What is the square of 12?")
```

### ⚡ Execution Modes (Auto-Routing)

The Agent features intelligent routing to save time and API costs on simple tasks. By default, it runs in `mode="auto"`.
- **`auto`**: The agent analyzes the prompt. If it's a simple question, it gives a direct answer. If it requires tools or multi-step logic, it spins up the planning loop.
- **`fast_ans`**: Forces the agent to skip planning and answer immediately using memory context.
- **`plan`**: Forces the agent into the rigorous `Think -> Plan -> Act -> Reflect` loop.

```python
# Forces a fast answer (Bypasses tool execution)
await agent.run("Hi, who are you?", mode="fast_ans")

# Forces complex planning
await agent.run("Search the web for the latest Python release...", mode="plan")
```

## 📖 Quickstart: RAG Pipeline

The `RAGPipeline` is the highest-level service for handling document-based knowledge.

```python
import asyncio
from phoenix import init_phoenix, startup_phoenix, get_rag_pipeline

async def rag_demo():
    init_phoenix()
    await startup_phoenix()
    rag = get_rag_pipeline()

    # 1. Ingest documents (Supports Docs + Source Code .py, .js, .go, .rs, etc.)
    await rag.ingest("./my_project")

    # 2. Ingest from GitHub Repository (Automated cloning & indexing)
    await rag.ingest_github("https://github.com/blackeagle686/phoenix-ai.git")

    # 3. Ingest from Web URL
    await rag.ingest_url("https://example.com/docs/api")

    # 4. Query with automatic Citations
    answer = await rag.query("How do I extend the cache layer?")
    print(f"AI Answer: {answer}")
```

### 🐦‍🔥 Source Attribution
The SDK now automatically instructs the LLM to cite its sources. When you query the RAG pipeline, the response will often include markers like `[Source: cloud.pdf]` or `[Source: https://example.com]`.

## ⚠️ Local Model Hardware Requirements
If you plan to use local inference (Ollama or Transformers), please ensure your system meets these specifications:
- **RAM**: 8GB Minimum (16GB+ recommended).
- **GPU**: 4GB+ VRAM required for VLM models (using 4-bit quantization).
- **Disk**: 10GB+ free space for model storage.

> [!WARNING]
> High-resource models may cause system instability on low-RAM or CPU-only devices. The SDK defaults to a safety-first approach and will prompt for confirmation before starting local providers.

## 🐦‍🔥 Dynamic Fallbacks & Native PyTorch

phoenix includes a robust "fail-loud and recover gracefully" orchestration architecture for AI providers:

### 1. Interactive Provider Fallbacks
If your primary provider (e.g. Local) fails to connect or crashes, the SDK's orchestration (`VLMPipeline` / `InsightEngine`) instantly intercepts the failure and prompts you to fallback to the secondary provider (e.g. OpenAI), bypassing pipeline crashes.

### 2. Native PyTorch Singleton Caching (`LocalVLM` & `LocalLLM`)
No `Ollama` server? No problem! The local providers automatically detect if Hugging Face `transformers` is installed and spin up models natively in your local GPU using an optimized Singleton cache.
> **Jupyter/Colab Tip**: If you face persistent `Ollama` warnings after installing `transformers`, run `LocalVLM._model_cache.clear()` or `LocalLLM._model_cache.clear()` in your notebook to wipe the previous state and force a PyTorch native reload.

### 3. Automatic 4-Bit Quantization
To prevent `CUDA Out of Memory` (OOM) errors on smaller GPUs (like Colab T4s), the SDK auto-detects `bitsandbytes` (`pip install bitsandbytes`) and instantly applies `load_in_4bit=True` to shrink massive models (like Qwen2-VL) into your VRAM.

### 4. Resilient RAG PDFs
The `RAGPipeline.ingest()` method supports PDFs robustly by sequentially testing for parsing libraries: `pypdf`, `pymupdf` (`fitz`), `pdfplumber`, and `PyPDF2`. Simply install whichever you prefer (`pip install pymupdf` is recommended for speed) and it works flawlessly!

## 🐦‍🔥 Advanced Usage: Insight Engine

The `InsightEngine` performs full context retrieval, query rewriting, and LLM generation efficiently.

```python
from phoenix import init_phoenix, get_insight_engine

async def insight_demo():
    init_phoenix()
    insight = get_insight_engine()

    # This invokes: Clean Query -> Vector Search -> Rerank -> LLM Generation
    final_response = await insight.query("How do I extend the cache layer?")
    print(final_response)
```

## 🖼️ Quickstart: VLM (Vision)

The `VLMPipeline` orchestrates vision tasks with automatic caching and RAG.

```python
from phoenix import init_phoenix_full, get_vlm_pipeline

async def vision_demo():
    await init_phoenix_full()
    vlm = get_vlm_pipeline()

    # Integrated: Result Caching + RAG context injection
    answer = await vlm.ask("What is in this image?", "image.png", use_rag=True)
    print(answer)
```
