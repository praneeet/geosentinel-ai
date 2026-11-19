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

def test_executive_summarizer_three_bullet_format():
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

def test_contextual_multi_country_attribution():
    """Verify actor vs affected country attribution in multi-country geopolitical news."""
    title = "Russian forces launched missile strikes targeting infrastructure in Ukraine"
    body = "Artillery and drone barrages struck Kharkiv regional energy facilities."
    attr = entity_extractor.extract_country_attributions(title, body)

    assert attr["primary_country_iso"] == "UKR"
    assert "UKR" in attr["affected_countries"]
    assert "RUS" in attr["actor_countries"]
    assert attr["is_multi_country"] is True
    assert attr["attribution_confidence"] > 0.65

def test_multi_country_diplomatic_attribution():
    """Verify primary country resolution does not blindly pick the first mentioned entity."""
    # US is mentioned first, but Taiwan is the affected theater of operations
    title = "United States dispatched military assistance package to Taiwan amid regional naval exercises"
    body = "Defense officials confirmed shipments intended to bolster Taiwan Strait defensive cordons."
    resolved = entity_extractor.resolve_primary_country(title, body)
    assert resolved == "TWN"

def test_classifier_uncertain_on_empty_or_vague_input():
    """Verify classifier returns UNCERTAIN rather than guessing on insufficient signals."""
    cat, conf, _ = classifier.predict("")
    assert cat == "UNCERTAIN"
    assert conf == 0.0

    cat2, conf2, _ = classifier.predict("Hello world today is a fine day.")
    assert cat2 == "UNCERTAIN"

def test_summarizer_title_only_factual_integrity():
    """Verify summarizer does not hallucinate kinetic escalation on title-only dispatches."""
    bullets = summarizer.generate_bullet_briefing(
        title="Bilateral negotiations concluded in Geneva",
        body_text="",
        category="DIPLOMACY",
        country_name="Switzerland",
    )
    assert len(bullets) == 3
    assert "Geneva" in bullets[0]
    # Bullet 2 should not invent casualties or military maneuvers
    assert "missile" not in bullets[1].lower()
    assert "casualt" not in bullets[1].lower()
