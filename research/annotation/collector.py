"""
GeoSentinel AI - 1,000-Article Real-World News Collector & Corpus Pipeline
Fetches authentic real-world news dispatches from open RSS/OSINT feeds,
extracts title, source attribution, collection timestamp, published timestamp,
and country hint, running MinHash LSH to ensure clean, non-duplicate corpus collection.
AKGEC Department of IT | CSIT Group 32
"""
import os
import sys
import json
import uuid
import hashlib
from datetime import datetime, timezone
import feedparser

base_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(base_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app.deduplication.minhash_lsh import deduplicator

REAL_WORLD_FEEDS = [
    {"source": "BBC World News", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "credibility": 0.95},
    {"source": "UN News Global", "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml", "credibility": 0.96},
    {"source": "Deutsche Welle World", "url": "https://rss.dw.com/rdf/rss-en-world", "credibility": 0.92},
    {"source": "Al Jazeera English", "url": "https://www.aljazeera.com/xml/rss/all.xml", "credibility": 0.90},
]

def collect_from_feeds(target_count: int = 1000, output_path: str = None) -> int:
    if output_path is None:
        output_path = os.path.join(base_dir, "corpus_1000.json")

    existing_articles = []
    seen_hashes = set()

    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_articles = json.load(f)
            for a in existing_articles:
                if "content_sha256" in a:
                    seen_hashes.add(a["content_sha256"])
            print(f"Loaded {len(existing_articles)} existing articles from {output_path}")
        except Exception as e:
            print(f"Error loading existing corpus: {e}")

    collected = list(existing_articles)
    now_iso = datetime.now(timezone.utc).isoformat()

    print(f"Initiating collection pipeline across {len(REAL_WORLD_FEEDS)} verified global feeds...")

    for feed_info in REAL_WORLD_FEEDS:
        if len(collected) >= target_count:
            break
        src_name = feed_info["source"]
        feed_url = feed_info["url"]
        credibility = feed_info["credibility"]

        try:
            feed = feedparser.parse(feed_url)
            print(f"Parsed {src_name}: found {len(feed.entries)} feed items.")

            for entry in feed.entries:
                if len(collected) >= target_count:
                    break

                title = entry.get("title", "").strip()
                summary = entry.get("summary", entry.get("description", "")).strip()
                link = entry.get("link", "")
                pub_date = entry.get("published", entry.get("updated", now_iso))

                full_text = f"{title}. {summary}".strip()
                if len(full_text) < 40:
                    continue

                # SHA-256 Content Hash
                chash = hashlib.sha256(full_text.encode("utf-8")).hexdigest()
                if chash in seen_hashes:
                    continue
                seen_hashes.add(chash)

                # MinHash LSH Near-Duplicate Check
                is_near_dup, _ = deduplicator.check_near_duplicate(full_text)
                if is_near_dup:
                    continue
                deduplicator.index_article(str(uuid.uuid4()), full_text)

                article_record = {
                    "article_id": str(uuid.uuid4()),
                    "source_name": src_name,
                    "source_url": link,
                    "source_credibility": credibility,
                    "published_at": pub_date,
                    "collected_at": now_iso,
                    "headline": title,
                    "body_text": full_text,
                    "country_iso": "GLOBAL",
                    "language": "en",
                    "content_sha256": chash,
                    "annotator_1_label": None,
                    "annotator_2_label": None,
                    "adjudicated_label": None,
                    "annotation_status": "collected",
                    "split": None,
                }
                collected.append(article_record)

        except Exception as e:
            print(f"Warning: error parsing feed {src_name}: {e}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(collected, f, indent=2)

    print(f"Corpus updated: {len(collected)} total articles stored at {output_path}")
    return len(collected)

if __name__ == "__main__":
    count = collect_from_feeds(target_count=1000)
    print(f"Collection pipeline complete. Current corpus count: {count}")
