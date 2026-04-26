from typing import Any, List, Optional, Dict
from abc import ABC, abstractmethod

class BaseMemory(ABC):
    """
    Base class for all memory components in Phoenix AI SDK.
    """
    
    @abstractmethod
    async def add(self, session_id: str, data: Any, metadata: Optional[Dict] = None) -> None:
        """Add data to memory for a given session."""
        pass

    @abstractmethod
    async def get(self, session_id: str, limit: int = 10) -> List[Any]:
        """Retrieve recent data from memory for a given session."""
        pass

    @abstractmethod
    async def clear(self, session_id: str) -> None:
        """Clear memory for a given session."""
        pass

    @abstractmethod
    async def search(self, session_id: str, query: str, limit: int = 5) -> List[Any]:
        """Search across memory for relevant information."""
        pass
