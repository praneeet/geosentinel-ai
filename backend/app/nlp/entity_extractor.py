import re
import logging
from typing import List, Dict, Optional, Tuple, Set, Any
from app.utils.iso_countries import resolve_country_iso, ALIAS_TO_ISO, COUNTRY_DATABASE

logger = logging.getLogger("geosentinel.nlp.entity_extractor")

class SpacyEntityExtractor:
    """
    spaCy NER Entity Extractor & Context-Aware Country Attribution Engine.
    Resolves ISO-3166 alpha-3 country attributions without blindly taking the first mention.
    Distinguishes:
      - Country affected / Event location
      - Country responsible / Actor
      - Mentioned countries
      - Attribution confidence and supporting textual evidence
    """
    def __init__(self):
        self.nlp = None
        self._load_spacy()

    def _load_spacy(self):
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            self.nlp = None

    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extracts structured entities (GPE, LOC, ORG, PERSON, NORP) from text."""
        entities = []
        if not text:
            return entities

        if self.nlp:
            try:
                doc = self.nlp(text[:3000])
                for ent in doc.ents:
                    if ent.label_ in ["GPE", "LOC", "ORG", "PERSON", "NORP"]:
                        entities.append({"text": ent.text, "label": ent.label_})
                if entities:
                    return entities
            except Exception as e:
                logger.debug(f"spaCy NER extraction fallback triggered: {e}")

        # Fast rule-based entity extraction fallback
        words = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)
        seen = set()
        for w in words:
            if len(w) > 2 and w not in seen:
                seen.add(w)
                low = w.lower()
                if low in ALIAS_TO_ISO or low.upper() in COUNTRY_DATABASE:
                    entities.append({"text": w, "label": "GPE"})
                elif any(org_kw in low for org_kw in ["ministry", "command", "council", "union", "treaty", "nato", "iaea"]):
                    entities.append({"text": w, "label": "ORG"})

        return entities

    def extract_country_attributions(
        self,
        title: str,
        body_text: str,
        country_hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Deep contextual geopolitical country attribution.
        Distinguishes primary theater, affected countries, actor countries, and mentioned countries.
        """
        clean_title = title or ""
        clean_body = body_text or ""
        combined_text = f"{clean_title} {clean_body[:2000]}"
        lowered_title = clean_title.lower()
        lowered_body = clean_body[:2000].lower()

        # 1. Resolve explicit country hint if provided
        if country_hint:
            resolved_hint = resolve_country_iso(country_hint)
            if resolved_hint and resolved_hint in COUNTRY_DATABASE:
                return {
                    "primary_country_iso": resolved_hint,
                    "affected_countries": [resolved_hint],
                    "actor_countries": [],
                    "mentioned_countries": [resolved_hint],
                    "attribution_confidence": 0.95,
                    "is_multi_country": False,
                    "supporting_evidence": f"Explicit verified country hint provided: {country_hint}",
                }

        # 2. Scan text for all candidate countries
        country_mentions: Dict[str, Dict[str, Any]] = {}

        def record_country(iso: str, weight: float, role: str, term: str):
            if iso not in COUNTRY_DATABASE and iso != "GLB":
                return
            if iso not in country_mentions:
                country_mentions[iso] = {
                    "total_score": 0.0,
                    "affected_score": 0.0,
                    "actor_score": 0.0,
                    "matched_terms": set(),
                }
            country_mentions[iso]["total_score"] += weight
            if role == "affected":
                country_mentions[iso]["affected_score"] += weight
            elif role == "actor":
                country_mentions[iso]["actor_score"] += weight
            country_mentions[iso]["matched_terms"].add(term)

        # Disputed and high-conflict regional indicators mapped to sovereign ISO
        special_regions = {
            "donbas": ("UKR", "affected"),
            "crimea": ("UKR", "affected"),
            "kharkiv": ("UKR", "affected"),
            "zaporizhzhia": ("UKR", "affected"),
            "kherson": ("UKR", "affected"),
            "kyiv": ("UKR", "affected"),
            "kiev": ("UKR", "affected"),
            "gaza": ("PSE", "affected"),
            "west bank": ("PSE", "affected"),
            "rafah": ("PSE", "affected"),
            "ramallah": ("PSE", "affected"),
            "tel aviv": ("ISR", "affected"),
            "taipei": ("TWN", "affected"),
            "taiwan strait": ("TWN", "affected"),
        }

        for term, (iso, role) in special_regions.items():
            pattern = r"\b" + re.escape(term) + r"\b"
            if re.search(pattern, lowered_title):
                record_country(iso, 4.0, role, term)
            elif re.search(pattern, lowered_body):
                record_country(iso, 2.0, role, term)

        # Contextual preposition patterns for affected/theater vs actor
        # Theater / Affected: in <country>, strikes on <country>, across <country>
        # Actor: <country> launched, <country> strikes, <country> warns
        for alias, iso in ALIAS_TO_ISO.items():
            pattern = r"\b" + re.escape(alias) + r"\b"

            # Check title matches (higher priority)
            if re.search(pattern, lowered_title):
                # Check if preceded by "in", "at", "across", "targeting"
                if re.search(r"\b(in|at|across|into|on|targeting)\s+" + re.escape(alias) + r"\b", lowered_title):
                    record_country(iso, 5.0, "affected", alias)
                elif re.search(re.escape(alias) + r"\s+(forces|troops|military|launched|fired|attacked|struck|deployed|sanctioned)\b", lowered_title):
                    record_country(iso, 4.0, "actor", alias)
                else:
                    record_country(iso, 3.0, "general", alias)

            # Check body matches
            elif re.search(pattern, lowered_body):
                if re.search(r"\b(in|at|across|into|on|targeting)\s+" + re.escape(alias) + r"\b", lowered_body):
                    record_country(iso, 2.5, "affected", alias)
                elif re.search(re.escape(alias) + r"\s+(forces|troops|military|launched|fired|attacked|struck|deployed|sanctioned)\b", lowered_body):
                    record_country(iso, 2.0, "actor", alias)
                else:
                    record_country(iso, 1.0, "general", alias)

        if not country_mentions:
            return {
                "primary_country_iso": "GLB",
                "affected_countries": [],
                "actor_countries": [],
                "mentioned_countries": [],
                "attribution_confidence": 0.30,
                "is_multi_country": False,
                "supporting_evidence": "No specific sovereign country entities identified in OSINT report.",
            }

        # Determine primary country: prioritize affected theater, then total score
        sorted_by_affected = sorted(
            country_mentions.items(),
            key=lambda x: (x[1]["affected_score"] * 1.5 + x[1]["total_score"]),
            reverse=True,
        )

        primary_iso, primary_meta = sorted_by_affected[0]
        all_mentioned = list(country_mentions.keys())
        affected = [iso for iso, meta in country_mentions.items() if meta["affected_score"] > 0]
        if not affected:
            affected = [primary_iso]
        actors = [iso for iso, meta in country_mentions.items() if meta["actor_score"] > 0 and iso != primary_iso]

        # Calculate attribution confidence
        top_score = primary_meta["total_score"]
        conf = min(0.98, max(0.60, 0.50 + 0.10 * top_score))

        matched_list = list(primary_meta["matched_terms"])
        evidence = f"Identified {primary_iso} via matched signals: {', '.join(matched_list[:3])}"

        return {
            "primary_country_iso": primary_iso,
            "affected_countries": affected,
            "actor_countries": actors,
            "mentioned_countries": all_mentioned,
            "attribution_confidence": round(conf, 3),
            "is_multi_country": len(all_mentioned) > 1,
            "supporting_evidence": evidence,
        }

    def resolve_primary_country(
        self,
        title: str,
        body_text: str,
        country_hint: Optional[str] = None,
    ) -> str:
        """
        Determines the primary ISO-3166 alpha-3 country code for the event.
        Maintains API compatibility by returning primary ISO.
        """
        attr = self.extract_country_attributions(
            title=title,
            body_text=body_text,
            country_hint=country_hint,
        )
        return attr["primary_country_iso"]

entity_extractor = SpacyEntityExtractor()
