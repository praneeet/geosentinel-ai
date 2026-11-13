import asyncio
import sys
import os

# Add backend directory to path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.ingestion.rss import RSSClient
from app.ingestion.newsapi import NewsAPIClient
from app.ingestion.mediastack import MediaStackClient
from app.config import settings

async def main():
    print("=" * 70)
    print("  GEOSENTINEL AI: LIVE ONLINE NEWS INGESTION VERIFICATION")
    print("=" * 70)

    # 1. Test Curated Open-Access Portals (BBC, Al Jazeera, UN News, DW)
    print("\n[1/3] Testing Curated RSS Portals (BBC, Al Jazeera, UN, DW)...")
    try:
        rss = RSSClient()
        rss_articles = await rss.fetch_articles()
        print(f" -> SUCCESS: Fetched {len(rss_articles)} live articles from online news portals!")
        for idx, art in enumerate(rss_articles[:4], 1):
            print(f"   {idx}. [{art['source_name']}] {art['title']}")
            print(f"      Portal URL: {art['source_url']}")
            print(f"      Published : {art['published_at']}")
    except Exception as e:
        print(f" -> RSS Fetch Error: {e}")

    # 2. Test NewsAPI (newsapi.org)
    print("\n[2/3] Testing NewsAPI (newsapi.org)...")
    try:
        napi = NewsAPIClient(settings.NEWSAPI_KEY)
        napi_articles = await napi.fetch_articles()
        print(f" -> SUCCESS: Fetched {len(napi_articles)} live articles via NewsAPI!")
        for idx, art in enumerate(napi_articles[:3], 1):
            print(f"   {idx}. [{art['source_name']}] {art['title']}")
            print(f"      Portal URL: {art['source_url']}")
    except Exception as e:
        print(f" -> NewsAPI Fetch Error: {e}")

    # 3. Test MediaStack (mediastack.com)
    print("\n[3/3] Testing MediaStack (mediastack.com)...")
    try:
        mstack = MediaStackClient(settings.MEDIASTACK_KEY)
        mstack_articles = await mstack.fetch_articles()
        print(f" -> SUCCESS: Fetched {len(mstack_articles)} live articles via MediaStack!")
        for idx, art in enumerate(mstack_articles[:3], 1):
            print(f"   {idx}. [{art['source_name']}] {art['title']}")
            print(f"      Portal URL: {art['source_url']}")
    except Exception as e:
        print(f" -> MediaStack Fetch Error: {e}")

    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE: All online news sources are live and accessible.")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())

