from datetime import datetime, timezone
from typing import List, Dict, Any
import httpx
from app.ingestion.base import BaseNewsSource
from app.config import settings

class GDELTClient(BaseNewsSource):
    """Adapter for GDELT 2.0 Global Knowledge Graph."""

    def __init__(self):
        super().__init__(name="GDELT 2.0", enabled=settings.GDELT_ENABLED)
        self.api_url = "https://api.gdeltproject.org/api/v2/doc/doc"

    async def fetch_articles(self) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []

        articles = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "query": "geopolitics OR military OR conflict OR sanctions",
                    "mode": "artlist",
                    "maxrecords": "15",
                    "format": "json",
                }
                resp = await client.get(self.api_url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("articles", []):
                        pub_str = item.get("seendate")
                        pub_dt = datetime.now(timezone.utc)
                        if pub_str and len(pub_str) >= 8:
                            try:
                                pub_dt = datetime.strptime(pub_str[:14], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
                            except Exception:
                                pass

                        articles.append({
                            "title": item.get("title", ""),
                            "body_text": item.get("title", ""),
                            "source_name": item.get("domain", "GDELT 2.0"),
                            "source_url": item.get("url", ""),
                            "published_at": pub_dt,
                            "credibility": 0.86,
                            "language": item.get("language", "en"),
                        })
        except Exception:
            pass
        return articles
