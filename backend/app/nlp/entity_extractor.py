import re
from typing import List, Dict, Optional, Tuple
from app.utils.iso_countries import resolve_country_iso, ALIAS_TO_ISO, COUNTRY_DATABASE

class SpacyEntityExtractor:
    """
    spaCy NER Entity Extractor & ISO-3166 alpha-3 Country Resolver.
    Extracts GPE, LOC, ORG, and PERSON entities and resolves the primary country.
    """
    def __init__(self):
        self.nlp = None
        self._load_spacy()

    def _load_spacy(self):
        try:
            import spacy
            # Try loading small english web model
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            self.nlp = None

    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extracts structured entities from text."""
        entities = []
        if not text:
            return entities

        if self.nlp:
            try:
                doc = self.nlp(text[:2500])
                for ent in doc.ents:
                    if ent.label_ in ["GPE", "LOC", "ORG", "PERSON", "NORP"]:
                        entities.append({"text": ent.text, "label": ent.label_})
                if entities:
                    return entities
            except Exception:
                pass

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

    def resolve_primary_country(
        self,
        title: str,
        body_text: str,
        country_hint: Optional[str] = None,
    ) -> str:
        """
        Determines the primary ISO-3166 alpha-3 country code for the event.
        Prioritizes:
        1. Explicit valid country hint if provided
        2. Entities found in headline / title
        3. Entities found in body text
        4. Fallback: 'USA' or 'GLB'
        """
        if country_hint:
            resolved_hint = resolve_country_iso(country_hint)
            if resolved_hint:
                return resolved_hint

        # Check title first for high-signal country mentions
        combined = f"{title} {body_text[:1000]}"
        entities = self.extract_entities(combined)

        for ent in entities:
            if ent["label"] in ["GPE", "LOC", "NORP"]:
                iso = resolve_country_iso(ent["text"])
                if iso:
                    return iso

        # Scan text for known country aliases
        lowered = combined.lower()
        for alias, iso in ALIAS_TO_ISO.items():
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, lowered):
                return iso

        return "GLB"

entity_extractor = SpacyEntityExtractor()
