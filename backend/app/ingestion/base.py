from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseNewsSource(ABC):
    """Abstract base adapter for all geopolitical news and event sources."""

    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled

    @abstractmethod
    async def fetch_articles(self) -> List[Dict[str, Any]]:
        """
        Polls the source asynchronously and yields raw article dictionaries.
        Must handle its own timeouts, errors, and rate limits gracefully.
        """
        pass
