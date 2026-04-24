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
    _model_cache = {}

    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.EMBEDDING_MODEL
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._load_model()
        return self._model

    def _load_model(self):
        if self.model_name not in SentenceTransformerEmbeddings._model_cache:
            if SentenceTransformer is None:
                raise ImportError(
                    "sentence-transformers is not installed. "
                    "Please install it using: pip install sentence-transformers"
                )
            print(f"[*] Initializing Embedding Model: {self.model_name}...")
            SentenceTransformerEmbeddings._model_cache[self.model_name] = SentenceTransformer(self.model_name)
            print(f"[+] Embedding Model Loaded into cache.")
        
        self._model = SentenceTransformerEmbeddings._model_cache[self.model_name]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        embedding = self.model.encode([text])[0]
        return embedding.tolist()
