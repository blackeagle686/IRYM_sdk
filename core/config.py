import os

class Config:
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.longcat.chat/openai")
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

    # Vector DB Config
    VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chroma")
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

    # Embedding Config
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Local LLM's Config
    LOCAL_LLM_TEXT_MODEL = os.getenv("LOCAL_LLM_TEXT_MODEL", "")
    LOCAL_LLM_EMBED_MODEL = os.getenv("LOCAL_LLM_EMBED_MODEL", "")
    LOCAL_VLM_MODEL = os.getenv("LOCAL_VLM_MODEL", "")
    
    
config = Config()
