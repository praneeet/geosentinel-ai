import re
import html
import unicodedata
from typing import Dict, Any
from app.deduplication.exact_sha256 import calculate_sha256

def sanitize_and_normalize_article(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes article text:
    - Decodes HTML entities
    - Strips leftover HTML tags
    - Unicode NFKC normalization
    - Collapses whitespaces
    - Computes content_hash (SHA-256)
    """
    raw_title = raw.get("title", "") or "Untitled Intelligence Report"
    raw_body = raw.get("body_text", "") or raw.get("description", "") or ""

    # Clean title
    clean_title = html.unescape(raw_title)
    clean_title = re.sub(r"<[^>]+>", "", clean_title)
    clean_title = unicodedata.normalize("NFKC", clean_title)
    clean_title = re.sub(r"\s+", " ", clean_title).strip()

    # Clean body
    clean_body = html.unescape(raw_body)
    clean_body = re.sub(r"<[^>]+>", " ", clean_body)
    clean_body = unicodedata.normalize("NFKC", clean_body)
    clean_body = re.sub(r"\s+", " ", clean_body).strip()

    # If body is short, supplement with title
    if len(clean_body) < 30:
        clean_body = f"{clean_title}. {clean_body}".strip()

    # Deterministic content hash from normalized title + body
    hash_text = f"{clean_title} {clean_body}"
    content_hash = calculate_sha256(hash_text)

    return {
        "title": clean_title,
        "body_text": clean_body,
        "content_hash": content_hash,
        "source_name": raw.get("source_name", "Open-Source Wire"),
        "source_url": raw.get("source_url", "https://geosentinel.ai/source"),
        "credibility": float(raw.get("credibility", 0.90)),
        "published_at": raw.get("published_at"),
        "language": raw.get("language", "en"),
        "author": raw.get("author"),
        "country_hint": raw.get("country_hint"),
    }
