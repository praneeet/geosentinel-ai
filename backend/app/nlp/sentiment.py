import re
from typing import Tuple

class SentimentAndSeverityAnalyzer:
    """
    Sentiment polarity analyzer in [-1.0, +1.0] and severity estimator in [0.0, 1.0].
    Distinguishes sentiment polarity from geopolitical risk severity.
    """
    def __init__(self):
        self._vader = None
        self._init_vader()

    def _init_vader(self):
        try:
            from nltk.sentiment.vader import SentimentIntensityAnalyzer
            import nltk
            try:
                nltk.data.find("sentiment/vader_lexicon.zip")
            except LookupError:
                nltk.download("vader_lexicon", quiet=True)
            self._vader = SentimentIntensityAnalyzer()
        except Exception:
            self._vader = None

    def analyze_sentiment(self, text: str) -> float:
        """
        Returns sentiment polarity in [-1.0, +1.0].
        -1.0: strongly negative
         0.0: neutral
        +1.0: strongly positive
        """
        if not text:
            return 0.0

        if self._vader:
            try:
                scores = self._vader.polarity_scores(text[:1500])
                return round(float(scores["compound"]), 3)
            except Exception:
                pass

        # Fallback lexicon scoring
        pos_words = {"peace", "accord", "treaty", "de-escalation", "relief", "rebuilding", "agreement", "cooperation", "success"}
        neg_words = {"attack", "strike", "casualty", "dead", "crisis", "escalation", "bomb", "missile", "war", "hostile", "disaster", "danger"}

        lowered = text.lower()
        pos_count = sum(len(re.findall(r"\b" + w + r"\b", lowered)) for w in pos_words)
        neg_count = sum(len(re.findall(r"\b" + w + r"\b", lowered)) for w in neg_words)

        diff = pos_count - neg_count
        tot = pos_count + neg_count
        if tot == 0:
            return -0.20  # Geopolitical news default baseline is mildly negative
        return round(max(-1.0, min(1.0, diff / tot)), 3)

    def calculate_severity(self, category: str, sentiment: float, text: str) -> float:
        """
        Calculates explainable severity in [0.0, 1.0]:
        Combines domain category baseline + negative sentiment magnitude + critical threat indicators.
        """
        cat_upper = category.upper()
        base_weights = {
            "CONFLICT": 0.70,
            "SECURITY": 0.55,
            "ECONOMY": 0.40,
            "DIPLOMACY": 0.25,
        }
        base = base_weights.get(cat_upper, 0.40)

        # High negative sentiment increases severity
        neg_boost = max(0.0, -sentiment) * 0.25

        # Critical threat keyword modifiers
        threat_keywords = [
            "ballistic", "nuclear", "fatalities", "casualties", "mass casualty",
            "invasion", "blackout", "critical infrastructure", "state of emergency",
            "evacuation", "embargo", "ultimatum", "retaliation"
        ]
        lowered = text.lower()
        threat_count = sum(1 for kw in threat_keywords if kw in lowered)
        threat_boost = min(0.20, threat_count * 0.05)

        severity = base + neg_boost + threat_boost
        return round(max(0.10, min(1.0, severity)), 2)

sentiment_analyzer = SentimentAndSeverityAnalyzer()
