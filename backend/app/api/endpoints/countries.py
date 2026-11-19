import math
import json
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.country_score import CountryScore
from app.models.event import Event
from app.models.article import Article
from app.models.summary import Summary
from app.models.risk_history import RiskScoreHistory
from app.schemas.risk import CountryRiskResponse, RiskHistoryPoint, ContributingFactors
from app.schemas.country import CountryDetailResponse, ExecutiveSummaryResponse
from app.schemas.event import EventWithArticle
from app.utils.iso_countries import COUNTRY_DATABASE, get_country_info
from app.scoring.explainability import format_risk_explanation
from app.forecasting.engine import forecasting_engine

router = APIRouter()

def ensure_dict(val):
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return {}
    if isinstance(val, dict):
        return val
    return {}

def ensure_list(val):
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            return []
    if isinstance(val, list):
        return val
    return []

@router.get("/countries")
async def list_countries(db: AsyncSession = Depends(get_db)):
    """Returns list of monitored countries with current risk index and coordinates."""
    stmt = select(CountryScore)
    res = await db.execute(stmt)
    scores = {s.country_iso: s for s in res.scalars().all()}

    output = []
    for iso, info in COUNTRY_DATABASE.items():
        score_obj = scores.get(iso)
        risk_val = score_obj.risk_index if score_obj else 0.0
        tier = score_obj.risk_tier if score_obj else "Low"
        event_cnt = score_obj.event_count if score_obj else 0
        output.append({
            "country_iso": iso,
            "country_name": info["name"],
            "region": info["region"],
            "lat": info["lat"],
            "lon": info["lon"],
            "risk_index": risk_val,
            "risk_tier": tier,
            "event_count": event_cnt,
        })
    return output

async def _fetch_recent_history_points(
    country_iso: str, db: AsyncSession, limit: int = 30
) -> List[float]:
    """Fetches real chronological risk history points from the database for forecasting."""
    hist_stmt = (
        select(RiskScoreHistory.risk_index)
        .where(RiskScoreHistory.country_iso == country_iso)
        .order_by(RiskScoreHistory.recorded_at.desc())
        .limit(limit)
    )
    hist_res = await db.execute(hist_stmt)
    rows = list(reversed(hist_res.scalars().all()))
    return [float(r) for r in rows if r is not None]


@router.get("/countries/{iso}/risk")
async def get_country_risk(iso: str, db: AsyncSession = Depends(get_db)):
    c_iso = iso.upper()
    info = get_country_info(c_iso)

    stmt = select(CountryScore).where(CountryScore.country_iso == c_iso)
    res = await db.execute(stmt)
    score_obj = res.scalars().first()

    if not score_obj:
        # If not yet scored, check if any events exist in the database for this country
        ev_stmt = (
            select(Event, Article.title, Article.source_name, Article.source_url)
            .join(Article, Event.article_id == Article.article_id)
            .where(Event.country_iso == c_iso)
        )
        ev_res = await db.execute(ev_stmt)
        events_found = ev_res.all()
        cnt = len(events_found)
        
        default_factors = {
            "conflict_score": 0.0,
            "security_score": 0.0,
            "economy_score": 0.0,
            "diplomacy_score": 0.0,
            "temporal_decay_factor": 1.0,
            "sentiment_magnitude": 0.0,
            "active_event_count": cnt,
            "top_event_ids": [],
        }

        # If events exist, calculate real category distribution
        if cnt > 0:
            cat_counts = {"CONFLICT": 0, "SECURITY": 0, "ECONOMY": 0, "DIPLOMACY": 0}
            for ev, _, _, _ in events_found:
                cat = (ev.category or "SECURITY").upper()
                cat_counts[cat] = cat_counts.get(cat, 0) + 1
            default_factors["conflict_score"] = round((cat_counts["CONFLICT"] / cnt) * 10.0, 2)
            default_factors["security_score"] = round((cat_counts["SECURITY"] / cnt) * 10.0, 2)
            default_factors["economy_score"] = round((cat_counts["ECONOMY"] / cnt) * 10.0, 2)
            default_factors["diplomacy_score"] = round((cat_counts["DIPLOMACY"] / cnt) * 10.0, 2)

        category_breakdown = {
            "Conflict": default_factors["conflict_score"],
            "Security": default_factors["security_score"],
            "Economy": default_factors["economy_score"],
            "Diplomacy": default_factors["diplomacy_score"],
            "CONFLICT": default_factors["conflict_score"],
            "SECURITY": default_factors["security_score"],
            "ECONOMY": default_factors["economy_score"],
            "DIPLOMACY": default_factors["diplomacy_score"],
        }

        return {
            "country_iso": c_iso,
            "country_name": info["name"],
            "risk_index": 0.0,
            "risk_tier": "Low",
            "decayed_agg": 0.0,
            "event_count": cnt,
            "calculated_at": datetime.now(timezone.utc),
            "contributing_factors": default_factors,
            "category_breakdown": category_breakdown,
            "latitude": info["lat"],
            "longitude": info["lon"],
            "forecast": forecasting_engine.generate_forecast(current_risk=0.0, days=7),
            "explanation": format_risk_explanation(info["name"], {
                "risk_index": 0.0,
                "risk_tier": "Low",
                "event_count": cnt,
                "contributing_factors": default_factors
            }),
        }

    raw_factors = ensure_dict(score_obj.contributing_factors)
    category_breakdown = {
        "Conflict": round(float(raw_factors.get("conflict_score", 0.0)), 2),
        "Security": round(float(raw_factors.get("security_score", 0.0)), 2),
        "Economy": round(float(raw_factors.get("economy_score", 0.0)), 2),
        "Diplomacy": round(float(raw_factors.get("diplomacy_score", 0.0)), 2),
        "CONFLICT": round(float(raw_factors.get("conflict_score", 0.0)), 2),
        "SECURITY": round(float(raw_factors.get("security_score", 0.0)), 2),
        "ECONOMY": round(float(raw_factors.get("economy_score", 0.0)), 2),
        "DIPLOMACY": round(float(raw_factors.get("diplomacy_score", 0.0)), 2),
    }

    explanation = format_risk_explanation(info["name"], {
        "risk_index": score_obj.risk_index,
        "risk_tier": score_obj.risk_tier,
        "event_count": score_obj.event_count,
        "contributing_factors": raw_factors
    })

    history_pts = await _fetch_recent_history_points(c_iso, db)

    return {
        "country_iso": c_iso,
        "country_name": info["name"],
        "risk_index": score_obj.risk_index,
        "risk_tier": score_obj.risk_tier,
        "decayed_agg": score_obj.decayed_agg,
        "event_count": score_obj.event_count,
        "calculated_at": score_obj.calculated_at,
        "contributing_factors": raw_factors,
        "category_breakdown": category_breakdown,
        "latitude": info["lat"],
        "longitude": info["lon"],
        "forecast": forecasting_engine.generate_forecast(
            current_risk=score_obj.risk_index,
            history_points=history_pts or None,
            days=7,
        ),
        "explanation": explanation,
    }

@router.get("/countries/{iso}/forecast")
async def get_country_forecast(iso: str, days: int = Query(7, ge=1, le=14), db: AsyncSession = Depends(get_db)):
    """7-day forward risk trajectory projection via Holt's Damped Linear Exponential Smoothing."""
    c_iso = iso.upper()
    stmt = select(CountryScore).where(CountryScore.country_iso == c_iso)
    res = await db.execute(stmt)
    score_obj = res.scalars().first()
    cur_risk = score_obj.risk_index if score_obj else 0.0
    history_pts = await _fetch_recent_history_points(c_iso, db)
    return forecasting_engine.generate_forecast(
        current_risk=cur_risk,
        history_points=history_pts or None,
        days=days,
    )

@router.get("/countries/{iso}/history", response_model=List[RiskHistoryPoint])
async def get_country_history(iso: str, days: int = Query(30, ge=1, le=90), db: AsyncSession = Depends(get_db)):
    """Provides historical time-series data for risk trajectory, volume, and categories."""
    c_iso = iso.upper()
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)

    stmt = select(CountryScore).where(CountryScore.country_iso == c_iso)
    res = await db.execute(stmt)
    score_obj = res.scalars().first()
    cur_risk = score_obj.risk_index if score_obj else 0.0

    # Query persistent historical scores from database
    hist_stmt = (
        select(RiskScoreHistory)
        .where(
            RiskScoreHistory.country_iso == c_iso,
            RiskScoreHistory.recorded_at >= cutoff,
        )
        .order_by(RiskScoreHistory.recorded_at.asc())
    )
    hist_res = await db.execute(hist_stmt)
    db_history = hist_res.scalars().all()

    if db_history:
        history = []
        for h in db_history:
            factors = ensure_dict(h.contributing_factors)
            history.append(
                RiskHistoryPoint(
                    timestamp=h.recorded_at,
                    risk_score=h.risk_index,
                    event_volume=max(0, h.event_count),
                    sentiment=round(factors.get("sentiment_magnitude", -0.20), 2),
                    conflict_share=round(factors.get("conflict_score", 0.0), 1),
                    security_share=round(factors.get("security_score", 0.0), 1),
                    economy_share=round(factors.get("economy_score", 0.0), 1),
                    diplomacy_share=round(factors.get("diplomacy_score", 0.0), 1),
                )
            )
        return history

    # If no historical series records exist but current score exists, return single observed point
    if score_obj:
        factors = ensure_dict(score_obj.contributing_factors)
        return [
            RiskHistoryPoint(
                timestamp=score_obj.calculated_at or now,
                risk_score=score_obj.risk_index,
                event_volume=max(0, score_obj.event_count),
                sentiment=round(factors.get("sentiment_magnitude", -0.20), 2),
                conflict_share=round(factors.get("conflict_score", 0.0), 1),
                security_share=round(factors.get("security_score", 0.0), 1),
                economy_share=round(factors.get("economy_score", 0.0), 1),
                diplomacy_share=round(factors.get("diplomacy_score", 0.0), 1),
            )
        ]

    # Return empty list honestly when no historical observations exist - never fabricate synthetic curves
    return []

@router.get("/countries/{iso}/summary", response_model=ExecutiveSummaryResponse)
async def get_country_summary(iso: str, db: AsyncSession = Depends(get_db)):
    c_iso = iso.upper()
    info = get_country_info(c_iso)

    stmt = select(Summary).where(Summary.country_iso == c_iso)
    res = await db.execute(stmt)
    summary_obj = res.scalars().first()

    if not summary_obj:
        # Check if there are recent events for this country to synthesize dynamic briefing
        ev_stmt = (
            select(Event, Article.title, Article.source_name, Article.source_url)
            .join(Article, Event.article_id == Article.article_id)
            .where(Event.country_iso == c_iso)
            .order_by(Event.timestamp.desc())
            .limit(3)
        )
        ev_res = await db.execute(ev_stmt)
        ev_rows = ev_res.all()
        
        evidence_links = []
        if ev_rows:
            primary_ev, p_title, p_src, p_url = ev_rows[0]
            if p_url:
                evidence_links.append({"title": p_title, "url": p_url, "source": p_src})

            bullet_points = [
                f"Key Development: {p_title} ({primary_ev.category} reported via {p_src}).",
                f"Strategic Significance: Geopolitical telemetry detects active {primary_ev.category.lower()} indicators with severity rating of {primary_ev.severity:.2f}.",
                f"Operational Implication: Heightened cross-border risk surveillance recommended across {info['name']} critical nodes.",
            ]
        else:
            bullet_points = [
                f"Key Development: Strategic surveillance active across {info['name']} sovereign territory.",
                "Strategic Significance: Regional telemetry indicators demonstrate nominal baseline risk.",
                "Operational Implication: Continuous OSINT monitoring active for emerging geopolitical signals.",
            ]

        return ExecutiveSummaryResponse(
            country_iso=c_iso,
            bullet_points=bullet_points,
            evidence_links=evidence_links,
            generated_at=datetime.now(timezone.utc),
            model_version="geosentinel-nlp-v2",
        )

    bullet_points = ensure_list(summary_obj.bullet_points)
    evidence_links = ensure_list(summary_obj.evidence_links)

    return ExecutiveSummaryResponse(
        country_iso=c_iso,
        bullet_points=bullet_points,
        evidence_links=evidence_links,
        generated_at=summary_obj.generated_at,
        model_version=summary_obj.model_version or "geosentinel-nlp-v2",
    )

@router.get("/countries/{iso}/events", response_model=List[EventWithArticle])
async def get_country_events(iso: str, limit: int = 15, db: AsyncSession = Depends(get_db)):
    c_iso = iso.upper()
    stmt = (
        select(Event, Article.title, Article.source_name, Article.source_url)
        .join(Article, Event.article_id == Article.article_id)
        .where(Event.country_iso == c_iso)
        .order_by(Event.timestamp.desc())
        .limit(limit)
    )
    res = await db.execute(stmt)

    events = []
    for ev, art_title, s_name, s_url in res.all():
        entities = ensure_list(ev.entities)
        events.append(
            EventWithArticle(
                event_id=ev.event_id,
                article_id=ev.article_id,
                category=ev.category,
                country_iso=ev.country_iso,
                sentiment=ev.sentiment,
                severity=ev.severity,
                entities=entities,
                timestamp=ev.timestamp,
                confidence=ev.confidence,
                model_version=ev.model_version,
                created_at=ev.created_at,
                article_title=art_title,
                source_name=s_name,
                source_url=s_url,
            )
        )
    return events
