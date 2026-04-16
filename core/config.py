import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

class Config:
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # LLM Config
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ak_2yp3Xw1Ny7ky2pF7er9x93ZO9jj6G")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.longcat.chat/openai")
    OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "LongCat-Flash-Chat")
    
    # VLM Config
    OPENAI_VLM_API_KEY = os.getenv("OPENAI_VLM_API_KEY", "")
    OPENAI_VLM_BASE_URL = os.getenv("OPENAI_VLM_BASE_URL", "")
    OPENAI_VLM_MODEL = os.getenv("OPENAI_VLM_MODEL", "")
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

    # Vector DB Config
    VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chroma")
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

    # Embedding Config
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Local LLM's Config
    LOCAL_LLM_TEXT_MODEL = os.getenv("LOCAL_LLM_TEXT_MODEL", "Qwen/Qwen2-1.5B-Instruct")
    LOCAL_LLM_EMBED_MODEL = os.getenv("LOCAL_LLM_EMBED_MODEL", "all-MiniLM-L6-v2")
    LOCAL_VLM_MODEL = os.getenv("LOCAL_VLM_MODEL", "Qwen/Qwen2-VL-2B-Instruct")
    
    # Fallback Behavior
    AUTO_ACCEPT_FALLBACK = os.getenv("AUTO_ACCEPT_FALLBACK", "false").lower() == "true"
    
config = Config()
