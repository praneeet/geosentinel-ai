import re
import hashlib
import unicodedata

def normalize_text_for_hash(text: str) -> str:
    """
    Normalizes article text for deterministic cryptographic hashing:
    1. Unicode NFKC normalization
    2. Lowercasing
    3. Removal of HTML tags if present
    4. Collapsing all whitespace sequences to single space
    5. Stripping leading/trailing whitespace
    """
    if not text:
        return ""
    # NFKC normal form
    norm = unicodedata.normalize("NFKC", text)
    # Remove HTML tags if present
    clean_html = re.sub(r"<[^>]+>", " ", norm)
    # Lowercase
    lowered = clean_html.lower()
    # Normalize whitespace
    collapsed = re.sub(r"\s+", " ", lowered).strip()
    return collapsed

def calculate_sha256(text: str) -> str:
    """Calculates SHA-256 hex digest of normalized article text."""
    normalized = normalize_text_for_hash(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
