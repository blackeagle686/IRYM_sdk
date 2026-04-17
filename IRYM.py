from typing import Any
from IRYM_sdk.core.container import container
from IRYM_sdk.core.config import config
from IRYM_sdk.cache.redis_cache import RedisCache
from IRYM_sdk.llm.openai import OpenAILLM
from IRYM_sdk.llm.local import LocalLLM
from IRYM_sdk.vector.chroma import ChromaVectorDB
from IRYM_sdk.vector.qdrant import QdrantVectorDB
from IRYM_sdk.vector.embeddings import SentenceTransformerEmbeddings
from IRYM_sdk.llm.vlm_openai import OpenAIVLM
from IRYM_sdk.llm.vlm_local import LocalVLM
from IRYM_sdk.insight.vlm_pipeline import VLMPipeline
from IRYM_sdk.insight.engine import InsightEngine
from IRYM_sdk.rag.pipeline import RAGPipeline
from IRYM_sdk.training.local_finetuner import LocalFineTuner
from IRYM_sdk.training.openai_finetuner import OpenAIFineTuner
from IRYM_sdk.memory.manager import MemoryManager
from IRYM_sdk.audio.local import LocalSTT, LocalTTS
from IRYM_sdk.audio.openai import OpenAISTT, OpenAITTS

def init_irym():
    # 1. Register Cache
    container.register("cache", RedisCache())
    
    # 2. Register LLM Providers
    container.register("llm_openai", OpenAILLM())
    container.register("llm_local", LocalLLM())
    
    # Compatibility mapping for generic 'llm'
    # Prefer OpenAI when API key, base URL and model are provided; otherwise use local
    try:
        llm_openai = container.get("llm_openai")
        llm_local = container.get("llm_local")
        if llm_openai.is_available():
            container.register("llm", llm_openai)
        elif llm_local.is_available():
            container.register("llm", llm_local)
        else:
            # Fallback to whatever was registered first
            container.register("llm", container.get("llm_local"))
    except Exception:
        container.register("llm", container.get("llm_local"))

    # 3. Register Embeddings
    embeddings = SentenceTransformerEmbeddings()
    container.register("embeddings", embeddings)

    # 4. Register VLM Providers
    container.register("vlm_openai", OpenAIVLM())
    container.register("vlm_local", LocalVLM())
    
    # Compatibility mapping for generic 'vlm'
    # Prefer OpenAI VLM when API key/base URL/model are provided; otherwise use local
    try:
        vlm_openai = container.get("vlm_openai")
        vlm_local = container.get("vlm_local")
        if vlm_openai.is_available():
            container.register("vlm", vlm_openai)
        elif vlm_local.is_available():
            container.register("vlm", vlm_local)
        else:
            container.register("vlm", container.get("vlm_local"))
    except Exception:
        container.register("vlm", container.get("vlm_local"))
    
    # 5. Register Vector DB based on config
    if config.VECTOR_DB_TYPE == "chroma":
        vector_db = ChromaVectorDB(embedding_service=embeddings)
    elif config.VECTOR_DB_TYPE == "qdrant":
        vector_db = QdrantVectorDB()
    else:
        raise ValueError(f"Unsupported vector DB type: {config.VECTOR_DB_TYPE}")
    
    container.register("vector_db", vector_db)

    # 6. Register Fine-Tuning Services
    container.register("finetune_local", LocalFineTuner())
    container.register("finetune_openai", OpenAIFineTuner())

    # 7. Register Memory Manager
    container.register("memory", MemoryManager(container.get("vector_db")))

    # 8. Register Audio Services
    container.register("stt_local", LocalSTT())
    container.register("stt_openai", OpenAISTT())
    container.register("tts_local", LocalTTS())
    container.register("tts_openai", OpenAITTS())

async def startup_irym():
    """
    Asynchronously initializes all services registered in the container.
    This includes Cache connections, Vector DB clients, and LLM pools.
    """
    # 1. Start Cache
    cache = container.get("cache")
    if hasattr(cache, "init"):
        await cache.init()
    
    # 2. Start LLM Providers
    llm_openai = container.get("llm_openai")
    llm_local = container.get("llm_local")
    if hasattr(llm_openai, "init"):
        await llm_openai.init()
    if hasattr(llm_local, "init"):
        await llm_local.init()
        
    # 3. Start Vector DB
    vector_db = container.get("vector_db")
    if hasattr(vector_db, "init"):
        await vector_db.init()
    
    # 4. Start VLM Providers
    vlm_openai = container.get("vlm_openai")
    vlm_local = container.get("vlm_local")
    if hasattr(vlm_openai, "init"):
        await vlm_openai.init()
    if hasattr(vlm_local, "init"):
        await vlm_local.init()
    
    # 5. Start Audio Services
    for service_name in ["stt_local", "stt_openai", "tts_local", "tts_openai"]:
        service = container.get(service_name)
        if hasattr(service, "init"):
            await service.init()
    
    print("[+] IRYM SDK Services started successfully.")

def get_rag_pipeline() -> RAGPipeline:
    vector_db = container.get("vector_db")
    llm_openai = container.get("llm_openai")
    llm_local = container.get("llm_local")
    cache = container.get("cache")
    return RAGPipeline(vector_db, primary=llm_local, fallback=llm_openai, cache=cache)

def get_insight_engine(openai_model: str = None, local_model: str = None, prefer_local: bool = True) -> InsightEngine:
    vector_db = container.get("vector_db")
    llm_openai = container.get("llm_openai")
    llm_local = container.get("llm_local")
    cache = container.get("cache")
    
    if openai_model:
        llm_openai.model = openai_model
    if local_model:
        llm_local.model = local_model
        
    if prefer_local:
        return InsightEngine(vector_db, llm_local, llm_openai, cache)
        
    return InsightEngine(vector_db, llm_openai, llm_local, cache)

def get_vlm_pipeline(openai_model: str = None, local_model: str = None, prefer_local: bool = True) -> VLMPipeline:
    vlm_openai = container.get("vlm_openai")
    vlm_local = container.get("vlm_local")
    vector_db = container.get("vector_db")
    cache = container.get("cache")
    
    # Dynamic overrides
    if openai_model:
        vlm_openai.model = openai_model
    if local_model:
        vlm_local.model = local_model
    
    if prefer_local:
        # Local is primary, OpenAI is fallback
        return VLMPipeline(vlm_local, vlm_openai, vector_db, cache)
    
    return VLMPipeline(vlm_openai, vlm_local, vector_db, cache)

def get_finetuner(provider: str = None) -> Any:
    """
    Returns the fine-tuning service based on provider ('local' or 'openai').
    Defaults to config.FINETUNE_PROVIDER.
    """
    provider = provider or config.FINETUNE_PROVIDER
    if provider == "openai":
        return container.get("finetune_openai")
    return container.get("finetune_local")

def get_llm() -> Any:
    return container.get("llm")

def get_memory() -> MemoryManager:
    return container.get("memory")

async def init_irym_full():
    """
    Complete initialization:
    1. init_irym (Registry)
    2. startup_irym (Connections)
    3. lifecycle.startup (Hooks)
    """
    from IRYM_sdk.core.lifecycle import lifecycle
    init_irym()
    await startup_irym()
    await lifecycle.startup()
    print("[+] IRYM SDK initialized and lifecycle hooks executed.")


def set_providers(llm_provider: str = None, vlm_provider: str = None) -> None:
    """
    Explicitly configure which provider to use for generic `llm` and `vlm`.

    llm_provider, vlm_provider: one of 'openai', 'local', or 'auto' (default 'auto').
    - 'openai' forces the OpenAI provider (may raise/print warnings if not available).
    - 'local' forces the Local provider.
    - 'auto' (or None) prefers OpenAI when available, otherwise local.

    Call this after `init_irym()` and before `startup_irym()` to customize behaviour.
    """
    # Helper to resolve a provider choice
    def resolve(choice, name_openai, name_local):
        if choice == "openai":
            return container.get(name_openai)
        if choice == "local":
            return container.get(name_local)
        # auto or None
        try:
            openai = container.get(name_openai)
            local = container.get(name_local)
            if hasattr(openai, "is_available") and openai.is_available():
                return openai
            return local
        except Exception:
            return container.get(name_local)

    if llm_provider is not None:
        llm = resolve(llm_provider, "llm_openai", "llm_local")
        container.register("llm", llm)

    if vlm_provider is not None:
        vlm = resolve(vlm_provider, "vlm_openai", "vlm_local")
        container.register("vlm", vlm)


def get_providers() -> dict:
    """Return currently configured generic providers for `llm` and `vlm`."""
    res = {}
    try:
        res["llm"] = container.get("llm")
    except Exception:
        res["llm"] = None
    try:
        res["vlm"] = container.get("vlm")
    except Exception:
        res["vlm"] = None
    return res
