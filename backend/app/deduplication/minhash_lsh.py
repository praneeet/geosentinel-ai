import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Set
from app.config import settings

class MinHashLSHDeduplicator:
    """
    Stage 2 Deduplication:
    MinHash with 128 permutations and Locality-Sensitive Hashing (LSH)
    Jaccard similarity threshold tau >= 0.82 within a 48-hour comparison window.
    Identifies syndicated, lightly modified, and wire service re-releases.
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
        self._lsh = None
        self._signatures: Dict[str, Tuple[datetime, any, Set[str]]] = {}
        self._init_lsh()

    def _init_lsh(self):
        try:
            from datasketch import MinHashLSH
            self._lsh = MinHashLSH(threshold=self.threshold, num_perm=self.num_perm)
        except ImportError:
            self._lsh = None

    def _generate_shingles(self, text: str) -> Set[str]:
        tokens = re.findall(r"\b\w+\b", text.lower())
        if len(tokens) < self.shingle_size:
            return set(tokens) if tokens else {"empty"}
        return {
            " ".join(tokens[i : i + self.shingle_size])
            for i in range(len(tokens) - self.shingle_size + 1)
        }

    def _compute_minhash(self, shingles: Set[str]):
        try:
            from datasketch import MinHash
            m = MinHash(num_perm=self.num_perm)
            for s in shingles:
                m.update(s.encode("utf-8"))
            return m
        except ImportError:
            return None

    def cleanup_old_window(self):
        """Purges signatures older than the 48-hour comparison window."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.window_hours)
        expired_keys = [
            k for k, (timestamp, _, _) in self._signatures.items() if timestamp < cutoff
        ]
        for k in expired_keys:
            if self._lsh is not None:
                try:
                    self._lsh.remove(k)
                except KeyError:
                    pass
            self._signatures.pop(k, None)

    def check_and_insert(
        self,
        article_id: str,
        text: str,
        published_at: Optional[datetime] = None,
    ) -> Tuple[str, Optional[str], float]:
        """
        Evaluates an article against the 48-hour LSH index.
        Returns:
            (dedup_status, canonical_article_id, max_similarity)
            where dedup_status is 'unique' or 'near_duplicate'
        """
        self.cleanup_old_window()
        timestamp = published_at or datetime.now(timezone.utc)
        shingles = self._generate_shingles(text)

        if self._lsh is not None:
            m = self._compute_minhash(shingles)
            if m is not None:
                # Check candidate matches via LSH and active window signatures
                for candidate_id, (_, candidate_m, _) in self._signatures.items():
                    if candidate_id == article_id or candidate_m is None:
                        continue
                    sim = m.jaccard(candidate_m)
                    if sim >= self.threshold:
                        return "near_duplicate", candidate_id, float(sim)

                # If unique, insert into index and signature store
                try:
                    self._lsh.insert(article_id, m)
                except Exception:
                    pass
                self._signatures[article_id] = (timestamp, m, shingles)
                return "unique", None, 0.0

        # Fallback pure-Python Jaccard if datasketch not yet loaded
        max_sim = 0.0
        best_match = None
        for candidate_id, (_, _, cand_shingles) in self._signatures.items():
            if not cand_shingles or not shingles:
                continue
            intersection = len(shingles & cand_shingles)
            union = len(shingles | cand_shingles)
            sim = (intersection / union) if union > 0 else 0.0
            if sim > max_sim:
                max_sim = sim
                best_match = candidate_id

        if max_sim >= self.threshold and best_match:
            return "near_duplicate", best_match, max_sim

        self._signatures[article_id] = (timestamp, None, shingles)
        return "unique", None, max_sim

deduplicator = MinHashLSHDeduplicator(
    threshold=settings.LSH_THRESHOLD,
    num_perm=settings.MINHASH_PERMUTATIONS,
    window_hours=settings.DEDUP_WINDOW_HOURS,
)
