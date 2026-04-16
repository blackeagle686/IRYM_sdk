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

def init_irym():
    # 1. Register Cache
    container.register("cache", RedisCache())
    
    # 2. Register LLM Providers
    container.register("llm_openai", OpenAILLM())
    container.register("llm_local", LocalLLM())
    
    # Compatibility mapping for generic 'llm'
    if config.LOCAL_LLM_TEXT_MODEL:
        container.register("llm", container.get("llm_local"))
    else:
        container.register("llm", container.get("llm_openai"))

    # 3. Register Embeddings
    embeddings = SentenceTransformerEmbeddings()
    container.register("embeddings", embeddings)

    # 4. Register VLM Providers
    container.register("vlm_openai", OpenAIVLM())
    container.register("vlm_local", LocalVLM())
    
    # Compatibility mapping for generic 'vlm'
    if config.LOCAL_VLM_MODEL:
        container.register("vlm", container.get("vlm_local"))
    else:
        container.register("vlm", container.get("vlm_openai"))
    
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
