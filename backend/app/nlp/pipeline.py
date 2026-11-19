from datetime import datetime, timezone
from typing import Dict, Any
from app.nlp.classifier import classifier
from app.nlp.entity_extractor import entity_extractor
from app.nlp.sentiment import sentiment_analyzer
from app.nlp.summarizer import summarizer
from app.utils.iso_countries import get_country_info

class NLPPipeline:
    """
    Unified NLP Pipeline:
    Transforms unstructured articles into structured geopolitical events
    tuples: (country, category, sentiment, severity, timestamp)
    plus 3-bullet executive briefings and entities.
    """
    def __init__(self):
        self.classifier = classifier
        self.entity_extractor = entity_extractor
        self.sentiment_analyzer = sentiment_analyzer
        self.summarizer = summarizer

    def process_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        title = article_data.get("title", "")
        body_text = article_data.get("body_text", "")
        country_hint = article_data.get("country_hint")
        combined_text = f"{title}\n{body_text}"

        # 1. Event Classification (TF-IDF + Calibrated Lexicon)
        category, confidence, model_ver = self.classifier.predict(combined_text)

        # 2. Entity Extraction & Context-Aware Country Attribution
        entities = self.entity_extractor.extract_entities(combined_text)
        attribution = self.entity_extractor.extract_country_attributions(
            title=title,
            body_text=body_text,
            country_hint=country_hint,
        )
        country_iso = attribution["primary_country_iso"]
        country_info = get_country_info(country_iso)

        # 3. Sentiment & Severity Analysis
        sentiment = self.sentiment_analyzer.analyze_sentiment(combined_text)
        severity = self.sentiment_analyzer.calculate_severity(
            category=category,
            sentiment=sentiment,
            text=combined_text,
        )

        # 4. Executive Summarization (Structured Briefing Engine)
        summary_result = self.summarizer.generate_structured_summary(
            title=title,
            body_text=body_text,
            category=category,
            country_name=country_info.get("name", country_iso),
        )

        return {
            "category": category,
            "confidence": confidence,
            "model_version": model_ver,
            "country_iso": country_iso,
            "country_name": country_info.get("name", country_iso),
            "affected_countries": attribution.get("affected_countries", [country_iso]),
            "actor_countries": attribution.get("actor_countries", []),
            "mentioned_countries": attribution.get("mentioned_countries", [country_iso]),
            "attribution_confidence": attribution.get("attribution_confidence", 0.85),
            "is_multi_country": attribution.get("is_multi_country", False),
            "attribution_evidence": attribution.get("supporting_evidence", ""),
            "sentiment": sentiment,
            "severity": severity,
            "entities": entities,
            "bullet_points": summary_result["bullet_points"],
            "timestamp": article_data.get("published_at") or datetime.now(timezone.utc),
        }

nlp_pipeline = NLPPipeline()
