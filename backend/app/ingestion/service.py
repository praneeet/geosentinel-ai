import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.ingestion.base import BaseNewsSource
from app.ingestion.normalizer import sanitize_and_normalize_article
from app.ingestion.newsapi import NewsAPIClient
from app.ingestion.mediastack import MediaStackClient
from app.ingestion.rss import RSSClient
from app.ingestion.gdelt import GDELTClient
from app.ingestion.demo_source import DemoSource
from app.deduplication.minhash_lsh import deduplicator
from app.nlp.pipeline import nlp_pipeline
from app.scoring.risk_engine import risk_engine
from app.models.article import Article
from app.models.event import Event
from app.models.country_score import CountryScore
from app.models.summary import Summary
from app.models.alert import Alert
from app.models.risk_history import RiskScoreHistory
from app.alerts.manager import alert_manager

logger = logging.getLogger("geosentinel.ingestion")

class IngestionService:
    """
    Asynchronous ETL & Ingestion Coordinator.
    Manages multi-source fetching, 2-stage deduplication, NLP event extraction,
    and automatic country risk recalculation with alert triggering.
    """

    def __init__(self):
        self.sources: List[BaseNewsSource] = []
        self._init_sources()

    def _init_sources(self):
        # Live external API sources (if credentials provided)
        if settings.NEWSAPI_KEY:
            self.sources.append(NewsAPIClient(settings.NEWSAPI_KEY))
        if settings.MEDIASTACK_KEY:
            self.sources.append(MediaStackClient(settings.MEDIASTACK_KEY))

        # Open-access news portals (BBC World News, Al Jazeera, UN News, Deutsche Welle)
        if settings.RSS_ENABLED:
            self.sources.append(RSSClient())
        if settings.GDELT_ENABLED:
            self.sources.append(GDELTClient())

        # Baseline fallback only if no live sources are configured
        if len(self.sources) == 0:
            self.sources.append(DemoSource())

    async def run_pipeline(self, session: AsyncSession) -> Dict[str, Any]:
        """
        Executes one full ingestion cycle across all configured sources.
        """
        raw_count = 0
        exact_dups = 0
        near_dups = 0
        unique_saved = 0
        events_created = 0
        affected_countries = set()

        for source in self.sources:
            try:
                articles = await source.fetch_articles()
                raw_count += len(articles)

                for raw_art in articles:
                    norm = sanitize_and_normalize_article(raw_art)
                    content_hash = norm["content_hash"]

                    # Stage 1: Exact SHA-256 check in DB
                    stmt = select(Article).where(Article.content_hash == content_hash)
                    res = await session.execute(stmt)
                    existing = res.scalars().first()
                    if existing:
                        exact_dups += 1
                        continue

                    # Stage 2: MinHash + LSH Near-Duplicate check
                    temp_id = str(uuid.uuid4())
                    dedup_status, canonical_id, sim = deduplicator.check_and_insert(
                        article_id=temp_id,
                        text=norm["body_text"],
                        published_at=norm.get("published_at"),
                    )

                    if dedup_status == "near_duplicate":
                        near_dups += 1
                        # We still persist near-duplicate for full auditability, linking to canonical article
                        article_obj = Article(
                            article_id=temp_id,
                            title=norm["title"],
                            content_hash=content_hash,
                            source_name=norm["source_name"],
                            source_url=norm["source_url"],
                            credibility=norm["credibility"],
                            published_at=norm["published_at"] or datetime.now(timezone.utc),
                            body_text=norm["body_text"],
                            language=norm["language"],
                            author=norm.get("author"),
                            country_hint=norm.get("country_hint"),
                            status="duplicate",
                            dedup_type="near_duplicate",
                            canonical_article_id=canonical_id,
                        )
                        session.add(article_obj)
                        await session.flush()
                        continue

                    # Unique Article -> Process through NLP pipeline
                    article_id = temp_id
                    article_obj = Article(
                        article_id=article_id,
                        title=norm["title"],
                        content_hash=content_hash,
                        source_name=norm["source_name"],
                        source_url=norm["source_url"],
                        credibility=norm["credibility"],
                        published_at=norm["published_at"] or datetime.now(timezone.utc),
                        body_text=norm["body_text"],
                        language=norm["language"],
                        author=norm.get("author"),
                        country_hint=norm.get("country_hint"),
                        status="processed",
                        dedup_type="unique",
                    )
                    session.add(article_obj)
                    await session.flush()
                    unique_saved += 1

                    # NLP Processing
                    nlp_res = nlp_pipeline.process_article(norm)
                    country_iso = nlp_res["country_iso"]
                    article_obj.country_hint = country_iso
                    affected_countries.add(country_iso)

                    # Save Event
                    event_obj = Event(
                        event_id=str(uuid.uuid4()),
                        article_id=article_id,
                        category=nlp_res["category"],
                        country_iso=country_iso,
                        sentiment=nlp_res["sentiment"],
                        severity=nlp_res["severity"],
                        entities=nlp_res["entities"],
                        timestamp=nlp_res["timestamp"],
                        confidence=nlp_res["confidence"],
                        model_version=nlp_res["model_version"],
                    )
                    session.add(event_obj)
                    events_created += 1

                    # Update or Insert Executive Summary
                    sum_stmt = select(Summary).where(Summary.country_iso == country_iso)
                    sum_res = await session.execute(sum_stmt)
                    existing_summary = sum_res.scalars().first()

                    evidence_item = {
                        "title": norm["title"],
                        "url": norm["source_url"],
                        "source": norm["source_name"],
                        "published_at": (norm["published_at"] or datetime.now(timezone.utc)).isoformat(),
                    }

                    if existing_summary:
                        existing_summary.bullet_points = nlp_res["bullet_points"]
                        cur_ev = list(existing_summary.evidence_links or [])
                        if not any(e.get("url") == norm["source_url"] for e in cur_ev):
                            cur_ev.insert(0, evidence_item)
                        existing_summary.evidence_links = cur_ev[:10]
                        existing_summary.generated_at = datetime.now(timezone.utc)
                    else:
                        new_summary = Summary(
                            summary_id=str(uuid.uuid4()),
                            country_iso=country_iso,
                            bullet_points=nlp_res["bullet_points"],
                            evidence_links=[evidence_item],
                            generated_at=datetime.now(timezone.utc),
                        )
                        session.add(new_summary)

            except Exception as e:
                logger.error(f"Error fetching from {source.name}: {str(e)}")
                continue

        await session.commit()

        # Recalculate Risk Scores for all affected countries
        alerts_triggered = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=settings.OBSERVATION_WINDOW_DAYS)
        for c_iso in affected_countries:
            if c_iso == "GLB":
                continue
            ev_stmt = (
                select(Event, Article.credibility)
                .join(Article, Event.article_id == Article.article_id)
                .where(
                    Event.country_iso == c_iso,
                    Event.timestamp >= cutoff,
                )
            )
            ev_res = await session.execute(ev_stmt)
            country_events = []
            for ev_row, cred in ev_res.all():
                country_events.append({
                    "event_id": ev_row.event_id,
                    "category": ev_row.category,
                    "sentiment": ev_row.sentiment,
                    "credibility": cred,
                    "timestamp": ev_row.timestamp,
                })

            risk_data = risk_engine.calculate_country_risk(country_events)

            # Update or create CountryScore
            score_stmt = select(CountryScore).where(CountryScore.country_iso == c_iso)
            score_res = await session.execute(score_stmt)
            existing_score = score_res.scalars().first()

            if existing_score:
                existing_score.risk_index = risk_data["risk_index"]
                existing_score.decayed_agg = risk_data["decayed_agg"]
                existing_score.risk_tier = risk_data["risk_tier"]
                existing_score.event_count = risk_data["event_count"]
                existing_score.contributing_factors = risk_data["contributing_factors"]
                existing_score.calculated_at = datetime.now(timezone.utc)
            else:
                new_score = CountryScore(
                    score_id=str(uuid.uuid4()),
                    country_iso=c_iso,
                    risk_index=risk_data["risk_index"],
                    decayed_agg=risk_data["decayed_agg"],
                    risk_tier=risk_data["risk_tier"],
                    event_count=risk_data["event_count"],
                    contributing_factors=risk_data["contributing_factors"],
                    calculated_at=datetime.now(timezone.utc),
                )
                session.add(new_score)

            # Record historical snapshot for longitudinal trends
            history_snapshot = RiskScoreHistory(
                history_id=str(uuid.uuid4()),
                country_iso=c_iso,
                risk_index=risk_data["risk_index"],
                risk_tier=risk_data["risk_tier"],
                event_count=risk_data["event_count"],
                contributing_factors=risk_data["contributing_factors"],
                recorded_at=datetime.now(timezone.utc),
            )
            session.add(history_snapshot)

            # Check Alert Trigger (R > 75)
            if risk_data["is_critical"]:
                alert_payload = await alert_manager.check_and_trigger(
                    country_iso=c_iso,
                    risk_score=risk_data["risk_index"],
                    tier=risk_data["risk_tier"],
                    contributing_factors=risk_data["contributing_factors"],
                    session=session,
                )
                if alert_payload:
                    alerts_triggered.append(alert_payload)

        await session.commit()

        duplication_rate = (
            ((exact_dups + near_dups) / raw_count * 100) if raw_count > 0 else 0.0
        )

        return {
            "status": "success",
            "raw_articles_fetched": raw_count,
            "exact_duplicates": exact_dups,
            "near_duplicates": near_dups,
            "unique_articles_saved": unique_saved,
            "events_created": events_created,
            "affected_countries_count": len(affected_countries),
            "duplication_rate_pct": round(duplication_rate, 2),
            "alerts_triggered_count": len(alerts_triggered),
            "alerts": alerts_triggered,
        }

ingestion_service = IngestionService()
