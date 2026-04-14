from abc import ABC, abstractmethod
from typing import List, Union, Optional
import numpy as np
from IRYM_sdk.core.config import config

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

class BaseEmbeddings(ABC):
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        pass

class SentenceTransformerEmbeddings(BaseEmbeddings):
    def __init__(self, model_name: str = None):
        model_to_use = model_name or config.EMBEDDING_MODEL
        print(f"[*] Initializing Embedding Model: {model_to_use}...")
        self.model = SentenceTransformer(model_to_use)
        print(f"[+] Embedding Model Loaded.")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        embedding = self.model.encode([text])[0]
        return embedding.tolist()
