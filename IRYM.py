from IRYM_sdk.core.container import container
from IRYM_sdk.core.config import config
from IRYM_sdk.cache.redis_cache import RedisCache
from IRYM_sdk.llm.openai import OpenAILLM
from IRYM_sdk.vector.chroma import ChromaVectorDB
from IRYM_sdk.vector.qdrant import QdrantVectorDB
from IRYM_sdk.vector.embeddings import SentenceTransformerEmbeddings
from IRYM_sdk.llm.vlm_openai import OpenAIVLM
from IRYM_sdk.llm.vlm_local import LocalVLM
from IRYM_sdk.insight.vlm_pipeline import VLMPipeline
from IRYM_sdk.insight.engine import InsightEngine

def init_irym():
    # Register Cache
    container.register("cache", RedisCache())
    
    # Register LLM
    container.register("llm", OpenAILLM())
    
    # Register Embeddings
    embeddings = SentenceTransformerEmbeddings()
    container.register("embeddings", embeddings)

    # Register VLM
    # Defaults to OpenAI if config doesn't specify local preference
    if config.LOCAL_VLM_MODEL:
        container.register("vlm", LocalVLM())
    else:
        container.register("vlm", OpenAIVLM())
    
    # Register Vector DB based on config
    if config.VECTOR_DB_TYPE == "chroma":
        vector_db = ChromaVectorDB(embedding_service=embeddings)
    elif config.VECTOR_DB_TYPE == "qdrant":
        vector_db = QdrantVectorDB()
    else:
        raise ValueError(f"Unsupported vector DB type: {config.VECTOR_DB_TYPE}")
    
    container.register("vector_db", vector_db)

async def startup_irym():
    """
    Asynchronously initializes all services registered in the container.
    This includes Cache connections, Vector DB clients, and LLM pools.
    """
    # 1. Start Cache
    cache = container.get("cache")
    if hasattr(cache, "init"):
        await cache.init()
    
    # 2. Start LLM
    llm = container.get("llm")
    if hasattr(llm, "init"):
        await llm.init()
        
    # 3. Start Vector DB
    vector_db = container.get("vector_db")
    if hasattr(vector_db, "init"):
        await vector_db.init()
    
    # 4. Start VLM
    vlm = container.get("vlm")
    if hasattr(vlm, "init"):
        await vlm.init()
    
    print("[+] IRYM SDK Services started successfully.")

def get_rag_pipeline() -> RAGPipeline:
    vector_db = container.get("vector_db")
    llm = container.get("llm")
    cache = container.get("cache")
    return RAGPipeline(vector_db, llm, cache)

def get_insight_engine() -> InsightEngine:
    vector_db = container.get("vector_db")
    llm = container.get("llm")
    cache = container.get("cache")
    return InsightEngine(vector_db, llm, cache)

def get_vlm_pipeline() -> VLMPipeline:
    vlm = container.get("vlm")
    vector_db = container.get("vector_db")
    cache = container.get("cache")
    return VLMPipeline(vlm, vector_db, cache)

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
