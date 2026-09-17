import pytest
from app.nlp.classifier import classifier
from app.nlp.entity_extractor import entity_extractor
from app.nlp.sentiment import sentiment_analyzer
from app.nlp.summarizer import summarizer
from app.utils.iso_countries import resolve_country_iso

def test_iso_country_resolution_aliases():
    assert resolve_country_iso("United States") == "USA"
    assert resolve_country_iso("US") == "USA"
    assert resolve_country_iso("U.S.A.") == "USA"
    assert resolve_country_iso("India") == "IND"
    assert resolve_country_iso("China") == "CHN"
    assert resolve_country_iso("Russia") == "RUS"
    assert resolve_country_iso("Ukraine") == "UKR"
    assert resolve_country_iso("Taiwan") == "TWN"
    assert resolve_country_iso("Israel") == "ISR"
    assert resolve_country_iso("Iran") == "IRN"

def test_classifier_categories():
    conflict_text = "Artillery shelling and missile strikes hit frontline command posts, causing casualties."
    cat, conf, ver = classifier.predict(conflict_text)
    assert cat == "CONFLICT"
    assert conf > 0.60

    economy_text = "Commerce department announced semiconductor export embargoes, tariffs, and currency inflation sanctions."
    cat2, conf2, _ = classifier.predict(economy_text)
    assert cat2 == "ECONOMY"

    diplomacy_text = "Envoys convened at the United Nations Security Council to negotiate a bilateral peace treaty and ceasefire accord."
    cat3, conf3, _ = classifier.predict(diplomacy_text)
    assert cat3 == "DIPLOMACY"

def test_sentiment_bounds():
    pos_text = "Delegates celebrated historic peaceful cooperation, reconstruction success, and mutual de-escalation relief."
    neg_text = "Brutal missile strikes caused mass casualties, severe destruction, disaster, and violent warfare."

    pos_score = sentiment_analyzer.analyze_sentiment(pos_text)
    neg_score = sentiment_analyzer.analyze_sentiment(neg_text)

    assert -1.0 <= pos_score <= 1.0
    assert -1.0 <= neg_score <= 1.0
    assert pos_score > neg_score

def test_bart_summarizer_three_bullet_format():
    bullets = summarizer.generate_bullet_briefing(
        title="Missile Interceptions Reported Over Coastal Port",
        body_text="Air defense radars detected multiple hostile unmanned vehicles approaching port logistics. Two vessels sustained minor fragment damage.",
        category="CONFLICT",
        country_name="Ukraine",
    )
    assert len(bullets) == 3
    assert bullets[0].startswith("Key development:")
    assert bullets[1].startswith("Strategic significance:")
    assert bullets[2].startswith("Geopolitical implication:")
