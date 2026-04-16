# IRYM SDK: The Complete Developer Guide

Welcome to the deep-dive guide for the IRYM SDK. This guide covers specific usage scenarios and integration patterns for building production AI applications.

---

## 🛠️ Core Service Guides

### 1. RAG (Retrieval Augmented Generation)
The RAG pipeline is the heart of document-based intelligence. It supports various file types and handles source attribution automatically.

```python
from IRYM_sdk import init_irym, startup_irym, get_rag_pipeline

async def run_rag():
    init_irym()
    await startup_irym()
    # Ingest from multiple sources
    await rag.ingest("./docs/")             # Files (PDF, MD, TXT, DOCX, XLSX)
    await rag.ingest_url("https://ai.com")  # Web Scraper
    
    # NEW: Advanced Ingestion
    await rag.ingest_sql(
        connection_string="sqlite:///data.db",
        query="SELECT content, author FROM posts",
        text_column="content"
    )
    
    await rag.ingest_api(
        url="https://api.service.com/v1/news",
        data_path="results.items"
    )
    
    # Query with citations
    response = await rag.query("How do I configure the vector store?")
    print(response) # "You can configure it in config.py... [Source: config.py]"
```

### 2. Audio Service (STT & TTS)
Handle voice interactions with local or cloud-based models.

#### 🎙️ Local Service
```python
from IRYM_sdk.audio.local import LocalAudioService
audio = LocalAudioService()
await audio.init()
text = await audio.stt("input.wav")
```

#### ☁️ OpenAI / Cloud Service
```python
from IRYM_sdk.audio.openai import OpenAISTT, OpenAITTS
stt = OpenAISTT()
tts = OpenAITTS()
await stt.init()
text = await stt.transcribe("voice.mp3")
```

### 3. VLM (Vision Language Models)
Analyze images using local or OpenAI-compatible vision models. The integrated pipeline handles **Caching** and **RAG context** automatically.

```python
from IRYM_sdk import init_irym_full, get_vlm_pipeline

async def vision_demo():
    await init_irym_full()
    vlm = get_vlm_pipeline()
    
    # 3-line integration: Model + Cache + RAG Context
    answer = await vlm.ask(
        prompt="Describe this scientific diagram.", 
        image_path="diagram.jpg",
        use_rag=True
    )
    print(answer)
```

### Service Fallback & Confirmation
IRYM SDK prioritizes your primary providers (OpenAI) but includes a robust fallback to local models (Ollama).

By default, the SDK is **Safety-First**: it will prompt you in the terminal for confirmation before starting a local model to avoid unexpected usage.

To change this behavior for production or non-interactive environments:
```bash
# .env
AUTO_ACCEPT_FALLBACK=true  # Automatically switch to local without asking
```

---

## 🏗️ Advanced Infrastructure

### 🔄 Lifecycle Management
Use the `LifecycleManager` to register hooks that run on application startup or shutdown. This is ideal for managing database pool connections or loading heavy AI models once.

```python
from IRYM_sdk.core.lifecycle import lifecycle

async def my_startup_task():
    print("Pre-loading resources...")

lifecycle.on_startup(my_startup_task)

# When your app starts:
await lifecycle.startup()
```

### 📊 Observability & Logging
Built-in structured logging for monitoring your AI services.

```python
from IRYM_sdk.observability.logger import get_logger
logger = get_logger("my_app")

logger.info("Starting AI processing...")
```

### 🚨 Error Handling
IRYM provides a typed exception hierarchy for robust error catching.

```python
from IRYM_sdk.core.exceptions import IRYMError, ServiceNotInitializedError

try:
    await rag.query("...")
except ServiceNotInitializedError:
    print("Forgot to call init()!")
```

---

## 🌐 Framework Integrations

### ⚡ FastAPI Integration
FastAPI's asynchronous nature is a perfect fit for IRYM. Use the lifecycle hooks for a clean setup.

```python
from fastapi import FastAPI
from IRYM_sdk import init_irym_full # New helper
from IRYM_sdk.core.lifecycle import lifecycle

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_irym_full() # Initializes config, DI, and runs lifecycle.startup()

@app.on_event("shutdown")
async def shutdown():
    await lifecycle.shutdown()
```

### 🎸 Django Integration
Integrate IRYM into your Django views.

```python
# views.py
from IRYM_sdk import get_rag_pipeline
import asyncio

def ai_chat(request):
    rag = get_rag_pipeline()
    answer = asyncio.run(rag.query(request.GET.get('q')))
    return JsonResponse({"answer": answer})
```

---

## 🧜‍♂️ System Architecture
```mermaid
graph TD
    A[User Request] --> B{Cache Check}
    B -- Hit --> C[Return Result]
    B -- Miss --> D[Vector Retrieval]
    D --> E[Prompt Composition]
    E --> F[LLM Generation]
    F --> G[Cache Result]
    G --> C
    
    subgraph Infrastructure
    D --- V[Chroma/Qdrant]
    B --- R[Redis]
    F --- L[LLM/VLM]
    end
```
