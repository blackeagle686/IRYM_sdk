from IRYM_sdk.core.container import container
from IRYM_sdk.core.config import config
from IRYM_sdk.cache.redis_cache import RedisCache
from IRYM_sdk.llm.openai import OpenAILLM
from IRYM_sdk.vector.chroma import ChromaVectorDB
from IRYM_sdk.vector.qdrant import QdrantVectorDB
from IRYM_sdk.vector.embeddings import SentenceTransformerEmbeddings
from IRYM_sdk.rag.pipeline import RAGPipeline
from IRYM_sdk.insight.engine import InsightEngine

def init_irym():
    # Register Cache
    container.register("cache", RedisCache())
    
    # Register LLM
    container.register("llm", OpenAILLM())
    
    # Register Embeddings
    embeddings = SentenceTransformerEmbeddings()
    container.register("embeddings", embeddings)
    
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
