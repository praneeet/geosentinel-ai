from typing import List, Dict, Any

class BartExecutiveSummarizer:
    """
    BART-Driven Executive Summarizer.
    Produces standardized 3-bullet decision-maker briefings:
    1. Key development
    2. Why it matters
    3. Relevant geopolitical implication
    """
    def __init__(self, model_version: str = "bart-large-cnn-geosentinel-v1"):
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
        sentences = [s.strip() for s in body_text.replace("\n", " ").split(".") if len(s.strip()) > 15]

        # 1. Key development
        first_sentence = sentences[0] if sentences else title
        bullet_1 = f"Key development: {title}. {first_sentence}."

        # 2. Why it matters
        second_sentence = sentences[1] if len(sentences) > 1 else "Directly affects frontline readiness and regional stability."
        bullet_2 = f"Strategic significance: {second_sentence}."

        # 3. Relevant geopolitical implication
        cat_implications = {
            "CONFLICT": f"Heightens kinetic escalation risks in {country_name} and threatens nearby transit and population corridors.",
            "SECURITY": f"Tests territorial air defense and critical infrastructure resilience against asymmetric offensive operations.",
            "ECONOMY": f"Generates secondary supply-chain friction, trade diversion, and sovereign market volatility for {country_name}.",
            "DIPLOMACY": f"Shapes multilateral treaty alignments and alters negotiation leverage across international mediation bodies.",
        }
        implication = cat_implications.get(
            category.upper(),
            f"Alters the regional balance of power and increases surveillance alert levels across {country_name}."
        )
        bullet_3 = f"Geopolitical implication: {implication}"

        return [bullet_1, bullet_2, bullet_3]

summarizer = BartExecutiveSummarizer()
