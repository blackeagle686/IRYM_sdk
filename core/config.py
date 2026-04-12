import os

class Config:
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.longcat.chat/openai")
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

    # Local LLM's Config
    LOCAL_LLM_TEXT_MODEL = os.getenv("LOCAL_LLM_TEXT_MODEL", "")
    LOCAL_LLM_EMBED_MODEL = os.getenv("LOCAL_LLM_EMBED_MODEL", "")
    LOCAL_VLM_MODEL = os.getenv("LOCAL_VLM_MODEL", "")
    
    
config = Config()
