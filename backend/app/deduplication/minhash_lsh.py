import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Set
from app.config import settings

import re
import threading
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Set, Any
from app.config import settings

logger = logging.getLogger("geosentinel.dedup.lsh")

class MinHashLSHDeduplicator:
    """
    Stage 2 Deduplication:
    MinHash with 128 permutations and Locality-Sensitive Hashing (LSH).
    Jaccard similarity threshold tau >= 0.82 within a 48-hour comparison window.
    Identifies syndicated, lightly modified, and wire service re-releases.
    Thread-safe with bounded memory consumption and transactional rollback support.
    """
    def __init__(
        self,
        threshold: float = 0.82,
        num_perm: int = 128,
        window_hours: int = 48,
        shingle_size: int = 2,
    ):
        self.threshold = threshold
        self.num_perm = num_perm
        self.window_hours = window_hours
        self.shingle_size = shingle_size
        self._lock = threading.Lock()
        self._lsh = None
        # Memory-efficient index: {article_id: (timestamp, minhash_obj)}
        self._signatures: Dict[str, Tuple[datetime, Any]] = {}
        self._init_lsh()

    def _init_lsh(self):
        try:
            from datasketch import MinHashLSH
            self._lsh = MinHashLSH(threshold=self.threshold, num_perm=self.num_perm)
        except ImportError:
            self._lsh = None

    def _generate_shingles(self, text: str) -> Set[str]:
        """Generates character/word n-gram shingles with short-text safety."""
        if not text or len(text.strip()) < 10:
            return set()
        tokens = re.findall(r"\b\w+\b", text.lower())
        if len(tokens) < self.shingle_size:
            return set()  # Do NOT generate synthetic {"empty"} - short texts cannot be near-duplicated
        return {
            " ".join(tokens[i : i + self.shingle_size])
            for i in range(len(tokens) - self.shingle_size + 1)
        }

    def _compute_minhash(self, shingles: Set[str]):
        if not shingles:
            return None
        try:
            from datasketch import MinHash
            m = MinHash(num_perm=self.num_perm)
            for s in shingles:
                m.update(s.encode("utf-8"))
            return m
        except ImportError:
            return None

    def cleanup_old_window(self):
        """Purges signatures older than the configured sliding comparison window."""
        with self._lock:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=self.window_hours)
            expired_keys = [
                k for k, (timestamp, _) in self._signatures.items() if timestamp < cutoff
            ]
            for k in expired_keys:
                if self._lsh is not None:
                    try:
                        self._lsh.remove(k)
                    except (KeyError, ValueError):
                        pass
                self._signatures.pop(k, None)

    def remove_signature(self, article_id: str):
        """Removes an uncommitted article from index during transaction rollback."""
        with self._lock:
            if self._lsh is not None:
                try:
                    self._lsh.remove(article_id)
                except (KeyError, ValueError):
                    pass
            self._signatures.pop(article_id, None)

    async def warmup_from_db(self, session) -> int:
        """
        Loads recent articles within the comparison window from the database
        to restore the in-memory LSH index after service restart.
        """
        try:
            from sqlalchemy import select
            from app.models.article import Article
            cutoff = datetime.now(timezone.utc) - timedelta(hours=self.window_hours)
            stmt = select(Article.article_id, Article.body_text, Article.published_at).where(
                Article.published_at >= cutoff,
                Article.status != "duplicate",
            )
            res = await session.execute(stmt)
            count = 0
            with self._lock:
                for aid, text, pub_at in res.all():
                    if aid not in self._signatures:
                        shingles = self._generate_shingles(text or "")
                        m = self._compute_minhash(shingles)
                        if m is not None and self._lsh is not None:
                            try:
                                self._lsh.insert(aid, m)
                            except Exception:
                                pass
                        pub_time = pub_at if pub_at and pub_at.tzinfo else datetime.now(timezone.utc)
                        self._signatures[aid] = (pub_time, m)
                        count += 1
            return count
        except Exception as e:
            logger.warning(f"Error warming LSH deduplicator index: {e}")
            return 0

    def check_and_insert(
        self,
        article_id: str,
        text: str,
        published_at: Optional[datetime] = None,
    ) -> Tuple[str, Optional[str], float]:
        """
        Evaluates an article against the 48-hour LSH index.
        Thread-safe execution.
        Returns:
            (dedup_status, canonical_article_id, max_similarity)
            where dedup_status is 'unique' or 'near_duplicate'
        """
        self.cleanup_old_window()
        timestamp = published_at or datetime.now(timezone.utc)
        shingles = self._generate_shingles(text)

        # Insufficient text length for near-duplicate indexing
        if not shingles:
            return "unique", None, 0.0

        with self._lock:
            if self._lsh is not None:
                m = self._compute_minhash(shingles)
                if m is not None:
                    try:
                        candidates = self._lsh.query(m)
                    except Exception:
                        candidates = []

                    best_sim = 0.0
                    best_candidate = None

                    for candidate_id in candidates:
                        if candidate_id == article_id:
                            continue
                        if candidate_id in self._signatures:
                            _, candidate_m = self._signatures[candidate_id]
                            if candidate_m is not None:
                                sim = m.jaccard(candidate_m)
                                if sim > best_sim:
                                    best_sim = sim
                                    best_candidate = candidate_id

                    # If threshold satisfied, return as near-duplicate
                    if best_sim >= self.threshold and best_candidate:
                        return "near_duplicate", best_candidate, float(best_sim)

                    # Fallback boundary check
                    if not best_candidate:
                        for candidate_id, (_, candidate_m) in self._signatures.items():
                            if candidate_id == article_id or candidate_m is None:
                                continue
                            sim = m.jaccard(candidate_m)
                            if sim >= self.threshold:
                                return "near_duplicate", candidate_id, float(sim)

                    # Unique: insert into LSH index and store signature
                    try:
                        self._lsh.insert(article_id, m)
                    except Exception:
                        pass
                    self._signatures[article_id] = (timestamp, m)
                    return "unique", None, float(best_sim)

            return "unique", None, 0.0

deduplicator = MinHashLSHDeduplicator(
    threshold=settings.LSH_THRESHOLD,
    num_perm=settings.MINHASH_PERMUTATIONS,
    window_hours=settings.DEDUP_WINDOW_HOURS,
)

deduplicator = MinHashLSHDeduplicator(
    threshold=settings.LSH_THRESHOLD,
    num_perm=settings.MINHASH_PERMUTATIONS,
    window_hours=settings.DEDUP_WINDOW_HOURS,
)
