from datetime import datetime, timezone
from typing import List, Dict, Any
import httpx
from app.ingestion.base import BaseNewsSource
from app.config import settings

class MediaStackClient(BaseNewsSource):
    """Adapter for MediaStack API."""

    def __init__(self, api_key: str = None):
        super().__init__(name="MediaStack", enabled=bool(api_key or settings.MEDIASTACK_KEY))
        self.api_key = api_key or settings.MEDIASTACK_KEY
        self.base_url = "http://api.mediastack.com/v1/news"

    async def fetch_articles(self) -> List[Dict[str, Any]]:
        if not self.enabled or not self.api_key:
            return []

        articles = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "access_key": self.api_key,
                    "languages": "en",
                    "limit": 25,
                    "categories": "general",
                }
                response = await client.get(self.base_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("data", []):
                        pub_str = item.get("published_at")
                        try:
                            pub_dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00")) if pub_str else datetime.now(timezone.utc)
                        except Exception:
                            pub_dt = datetime.now(timezone.utc)

                        articles.append({
                            "title": item.get("title", ""),
                            "body_text": item.get("description", ""),
                            "source_name": item.get("source", "MediaStack"),
                            "source_url": item.get("url", ""),
                            "published_at": pub_dt,
                            "author": item.get("author"),
                            "credibility": 0.88,
                            "language": item.get("language", "en"),
                            "country_hint": item.get("country"),
                        })
        except Exception:
            pass
        return articles
