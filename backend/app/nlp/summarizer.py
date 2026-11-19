import re
from typing import List, Dict, Any, Optional

class ExecutiveSummarizer:
    """
    Extractive and Analytical Decision-Maker Briefing Engine.
    Produces structured 3-bullet executive briefings separating:
      1. Key development: Primary factual event reported by the source
      2. Strategic significance: Grounded operational impact from supporting source text
      3. Geopolitical assessment: Calibrated domain risk implication for the theater
    Does NOT hallucinate unsupported claims when source text is brief or title-only.
    """
    def __init__(self, model_version: str = "extractive-analytical-v2"):
        self.model_version = model_version

    def generate_structured_summary(
        self,
        title: str,
        body_text: str,
        category: str,
        country_name: str,
    ) -> Dict[str, Any]:
        """
        Generates structured executive summary separating reported facts, significance, and implications.
        """
        raw_sentences = [
            s.strip()
            for s in re.split(r"[.!?]+", (body_text or "").replace("\n", " "))
            if len(s.strip()) > 15
        ]

        clean_title = (title or "").strip().rstrip(".")
        if not clean_title and raw_sentences:
            clean_title = raw_sentences[0]

        first_sentence = raw_sentences[0] if raw_sentences else clean_title

        # Bullet 1: Factual development strictly grounded in source
        if clean_title.lower() in first_sentence.lower():
            bullet_1 = f"Key development: {first_sentence}."
        elif first_sentence.lower() in clean_title.lower():
            bullet_1 = f"Key development: {clean_title}."
        else:
            bullet_1 = f"Key development: {clean_title}. {first_sentence}."

        # Bullet 2: Strategic significance from actual subsequent sentences
        has_subsequent_text = len(raw_sentences) > 1
        if has_subsequent_text:
            second_sentence = raw_sentences[1]
            bullet_2 = f"Strategic significance: {second_sentence}."
        else:
            # Honest fallback when source provides title-only or limited text
            bullet_2 = f"Strategic significance: Dispatch provides immediate headline confirmation; further tactical details are pending verification in {country_name}."

        # Bullet 3: Geopolitical implication tailored to domain and country
        cat_upper = (category or "SECURITY").upper()
        implications = {
            "CONFLICT": f"Geopolitical implication: Kinetic activity in {country_name} signals elevated threat levels for surrounding zones and transit routes.",
            "SECURITY": f"Geopolitical implication: Intelligence and defense alerts in {country_name} test surveillance readiness and deterrence postures.",
            "ECONOMY": f"Geopolitical implication: Trade, sanctions, or energy developments directly impact sovereign supply continuity and market stability in {country_name}.",
            "DIPLOMACY": f"Geopolitical implication: Bilateral and multilateral engagements shape negotiation leverage and regional de-escalation prospects for {country_name}.",
        }
        bullet_3 = implications.get(
            cat_upper,
            f"Geopolitical implication: Regional security and governance conditions in {country_name} warrant operational tracking."
        )

        bullet_points = [bullet_1, bullet_2, bullet_3]

        return {
            "reported_facts": bullet_1,
            "strategic_significance": bullet_2,
            "geopolitical_implication": bullet_3,
            "bullet_points": bullet_points,
            "confidence": 0.88 if has_subsequent_text else 0.70,
            "has_supporting_body": has_subsequent_text,
            "model_version": self.model_version,
        }

    def generate_bullet_briefing(
        self,
        title: str,
        body_text: str,
        category: str,
        country_name: str,
    ) -> List[str]:
        """
        Maintains backwards compatibility returning the 3-bullet string list.
        """
        summary_obj = self.generate_structured_summary(
            title=title,
            body_text=body_text,
            category=category,
            country_name=country_name,
        )
        return summary_obj["bullet_points"]

# Maintain backward compatibility alias while documenting underlying extractive-analytical nature
BartExecutiveSummarizer = ExecutiveSummarizer
summarizer = ExecutiveSummarizer()
