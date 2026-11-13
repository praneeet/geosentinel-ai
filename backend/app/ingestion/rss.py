from datetime import datetime, timezone
from typing import List, Dict, Any
import feedparser
import httpx
from app.ingestion.base import BaseNewsSource
from app.config import settings

CURATED_RSS_FEEDS = [
    {"name": "BBC World News", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "credibility": 0.95},
    {"name": "Al Jazeera English", "url": "https://www.aljazeera.com/xml/rss/all.xml", "credibility": 0.92},
    {"name": "UN News Global", "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml", "credibility": 0.98},
    {"name": "Deutsche Welle World", "url": "https://rss.dw.com/rdf/rss-en-world", "credibility": 0.94},
    {"name": "France 24 World", "url": "https://www.france24.com/en/rss", "credibility": 0.93},
    {"name": "The Guardian World", "url": "https://www.theguardian.com/world/rss", "credibility": 0.94},
    {"name": "NPR World News", "url": "https://feeds.npr.org/1004/rss.xml", "credibility": 0.94},
    {"name": "Sky News World", "url": "https://feeds.skynews.com/feeds/rss/world.xml", "credibility": 0.91},
]

class RSSClient(BaseNewsSource):
    """Adapter for open-access curated RSS feeds."""

    def __init__(self):
        super().__init__(name="Curated RSS", enabled=settings.RSS_ENABLED)
        self.feeds = CURATED_RSS_FEEDS

    async def fetch_articles(self) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []

        articles = []
        async with httpx.AsyncClient(timeout=8.0) as client:
            for feed_info in self.feeds:
                try:
                    resp = await client.get(feed_info["url"], follow_redirects=True)
                    if resp.status_code == 200:
                        parsed = feedparser.parse(resp.text)
                        for entry in parsed.entries[:30]:
                            title = entry.get("title", "")
                            summary = entry.get("summary") or entry.get("description") or ""
                            link = entry.get("link", "")
                            pub_dt = datetime.now(timezone.utc)
                            if hasattr(entry, "published_parsed") and entry.published_parsed:
                                pub_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

                            if title:
                                articles.append({
                                    "title": title,
                                    "body_text": summary,
                                    "source_name": feed_info["name"],
                                    "source_url": link,
                                    "published_at": pub_dt,
                                    "author": entry.get("author"),
                                    "credibility": feed_info["credibility"],
                                    "language": "en",
                                })
                except Exception:
                    # Skip problematic individual feed
                    continue

        return articles
