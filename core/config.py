import os

class Config:
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.longcat.chat/openai")
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    
config = Config()
