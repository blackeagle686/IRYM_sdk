from IRYM_sdk.core.container import container
from IRYM_sdk.cache.redis_cache import RedisCache
from IRYM_sdk.llm.openai import OpenAILLM
from IRYM_sdk.vector.qdrant import QdrantVectorDB

def init_irym():
    container.register("cache", RedisCache())
    container.register("llm", OpenAILLM())
    container.register("vector_db", QdrantVectorDB())
