# 🧠 IRYM_sdk (I can Read Your Mind SDK)

A production-ready, modular backend infrastructure SDK designed for AI-powered Python backend services. 

Whether you are building with FastAPI, Django, or a custom event-driven service, **IRYM_sdk** eliminates repetitive backend setup. It provides a unified, interchangeable system for caching, database access, background jobs, LLM integrations, vector databases, and RAG pipelines.

## 🏗️ Architecture Flow

The entire SDK is built around an **Everything is a Service** and **Interface-First** philosophy. Services are centrally managed by a Dependency Injection (DI) system, ensuring complete modularity and avoiding global state collision.

```mermaid
graph TD
    APP[Host Application e.g., FastAPI/Django] -->|Initializes| INIT(IRYM.py Initializer)
    APP -->|Requests Service via get()| DI{DI Container}
    INIT -->|Registers Services| DI
    
    subgraph Core
        DI
        CONF[Config & Settings]
        LFC[Lifecycle Hooks]
    end
    
    subgraph General Infrastructure
        DI -->|Provides| CACHE[Cache Service<br>RedisCache]
        DI -->|Provides| DB[DB Service<br>SQLAlchemyDB]
        DI -->|Provides| QUEUE[Queue Service<br>CeleryQueue]
    end
    
    subgraph AI & Data Operations
        DI -->|Provides| LLM[LLM Service<br>OpenAI/Local]
        DI -->|Provides| VDB[Vector DB<br>QdrantVectorDB]
        DI -->|Provides| RAG[RAG Pipeline]
        
        RAG -->|Retrieves context from| VDB
        RAG -->|Generates answer via| LLM
    end
    
    subgraph Observability
        OBS[Logger & Tracer] -.->|Monitors| CACHE
        OBS -.->|Monitors| DB
        OBS -.->|Monitors| LLM
        OBS -.->|Monitors| VDB
    end
```

## 🚀 Key Requirements & Core Features

1. **Dependency Injection**: Central standard registry. No manual instantiation inside business logic.
2. **Interface First**: Every module complies with an asynchronous base contract (`BaseCache`, `BaseLLM`, `BaseVectorDB`, etc.).
3. **Async-first**: Built iteratively to support high-throughput `asyncio` ecosystems.
4. **Clean AI Architecture**: Combines language models and vector environments effortlessly into `RAGPipeline` implementations.

## 🛠️ Usage Example

Easily inject `IRYM_sdk` logic inside FastAPI or Django:

```python
from fastapi import FastAPI
from IRYM_sdk import init_irym
from IRYM_sdk.core.container import container

app = FastAPI()

# 1. Initialize and register SDK services
init_irym()

@app.get("/test")
async def test():
    # 2. Safely grab configured instances from the container
    cache = container.get("cache")
    llm = container.get("llm")
    
    # 3. Use abstract base methods without worrying about inner details
    await cache.set("hello", {"msg": "world"}, ttl=60)
    cached_val = await cache.get("hello")
    
    response = await llm.generate("Hello world!")
    
    return {
        "cache_result": cached_val,
        "llm_response": response
    }
```
