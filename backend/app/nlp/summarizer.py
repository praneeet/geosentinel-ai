import re
from typing import List, Dict, Any

class ExecutiveSummarizer:
    """
    Extractive Executive Summarizer.
    Produces standardized 3-bullet decision-maker briefings:
    1. Key development: Primary factual event and theater
    2. Strategic significance: Operational/tactical impact
    3. Geopolitical implication: Regional balance of power and risk exposure
    """
    def __init__(self, model_version: str = "extractive-briefing-v1"):
        self.model_version = model_version

    def generate_bullet_briefing(
        self,
        title: str,
        body_text: str,
        category: str,
        country_name: str,
    ) -> List[str]:
        """
        Generates structured 3-bullet executive briefing.
        """
        raw_sentences = [
            s.strip()
            for s in re.split(r"[.!?]+", body_text.replace("\n", " "))
            if len(s.strip()) > 15
        ]

        clean_title = title.strip().rstrip(".")
        first_sentence = raw_sentences[0] if raw_sentences else clean_title

        # Avoid repeating the title if the first sentence is identical or an excerpt
        if clean_title.lower() in first_sentence.lower():
            bullet_1 = f"Key development: {first_sentence}."
        elif first_sentence.lower() in clean_title.lower():
            bullet_1 = f"Key development: {clean_title}."
        else:
            bullet_1 = f"Key development: {clean_title}. {first_sentence}."

        # Strategic significance from subsequent operational sentences
        if len(raw_sentences) > 1:
            second_sentence = raw_sentences[1]
            bullet_2 = f"Strategic significance: {second_sentence}."
        else:
            default_significance = {
                "CONFLICT": f"Alters frontline force disposition and active threat postures in {country_name}.",
                "SECURITY": f"Tests critical infrastructure defense readiness and intelligence monitoring.",
                "ECONOMY": f"Disrupts trade route reliability and impacts bilateral capital flows.",
                "DIPLOMACY": f"Signals diplomatic posturing and realignment across regional alliances.",
            }
            bullet_2 = f"Strategic significance: {default_significance.get(category.upper(), 'Directly influences regional operational readiness.')}"

        # Geopolitical implication tailored by domain
        cat_implications = {
            "CONFLICT": f"Heightens kinetic escalation risks in {country_name} and threatens nearby transit and population corridors.",
            "SECURITY": f"Tests territorial air defense and critical infrastructure resilience against asymmetric offensive operations in {country_name}.",
            "ECONOMY": f"Generates secondary supply-chain friction, trade diversion, and sovereign market volatility for {country_name}.",
            "DIPLOMACY": f"Shapes multilateral treaty alignments and alters negotiation leverage across international mediation bodies involving {country_name}.",
        }
        implication = cat_implications.get(
            category.upper(),
            f"Alters the regional balance of power and increases surveillance alert levels across {country_name}."
        )
        bullet_3 = f"Geopolitical implication: {implication}"

        return [bullet_1, bullet_2, bullet_3]

# Maintain backward compatibility aliases
BartExecutiveSummarizer = ExecutiveSummarizer
summarizer = ExecutiveSummarizer()
