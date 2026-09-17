import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.ingestion.base import BaseNewsSource

class DemoSource(BaseNewsSource):
    """Adapter that loads verified sample articles for offline academic demonstrations."""

    def __init__(self, filepath: str = None):
        super().__init__(name="Demo Dataset", enabled=True)
        # Search possible sample data locations
        self.filepath = filepath or os.path.join(os.path.dirname(__file__), "../../../data/samples/demo_articles.json")

    async def fetch_articles(self) -> List[Dict[str, Any]]:
        articles = []
        if not os.path.exists(self.filepath):
            # Try alternate path relative to workspace root
            alt = os.path.abspath("data/samples/demo_articles.json")
            if os.path.exists(alt):
                self.filepath = alt
            else:
                return []

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    pub_str = item.get("published_at")
                    try:
                        pub_dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00")) if pub_str else datetime.now(timezone.utc)
                    except Exception:
                        pub_dt = datetime.now(timezone.utc)

                    articles.append({
                        "title": item.get("title", ""),
                        "body_text": item.get("body_text", ""),
                        "source_name": f"[DEMO] {item.get('source_name', 'Wire')}",
                        "source_url": item.get("source_url", "https://geosentinel.ai/demo"),
                        "published_at": pub_dt,
                        "author": item.get("author"),
                        "credibility": float(item.get("credibility", 0.90)),
                        "language": item.get("language", "en"),
                        "country_hint": item.get("country_hint"),
                    })
        except Exception:
            pass
        return articles
