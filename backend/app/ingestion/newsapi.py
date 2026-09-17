from datetime import datetime, timezone
from typing import List, Dict, Any
import httpx
from app.ingestion.base import BaseNewsSource
from app.config import settings

class NewsAPIClient(BaseNewsSource):
    """Adapter for NewsAPI (newsapi.org)."""

    def __init__(self, api_key: str = None):
        super().__init__(name="NewsAPI", enabled=bool(api_key or settings.NEWSAPI_KEY))
        self.api_key = api_key or settings.NEWSAPI_KEY
        self.base_url = "https://newsapi.org/v2/top-headlines"

    async def fetch_articles(self) -> List[Dict[str, Any]]:
        if not self.enabled or not self.api_key:
            return []

        articles = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "apiKey": self.api_key,
                    "category": "general",
                    "language": "en",
                    "pageSize": 25,
                }
                response = await client.get(self.base_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("articles", []):
                        pub_str = item.get("publishedAt")
                        try:
                            pub_dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00")) if pub_str else datetime.now(timezone.utc)
                        except Exception:
                            pub_dt = datetime.now(timezone.utc)

                        articles.append({
                            "title": item.get("title", ""),
                            "body_text": item.get("content") or item.get("description") or "",
                            "source_name": item.get("source", {}).get("name", "NewsAPI"),
                            "source_url": item.get("url", ""),
                            "published_at": pub_dt,
                            "author": item.get("author"),
                            "credibility": 0.92,
                            "language": "en",
                        })
        except Exception as e:
            # Fallback gracefully on quota or network error
            pass
        return articles
