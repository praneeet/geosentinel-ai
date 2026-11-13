import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.models.event import Event
from app.models.article import Article
from app.schemas.event import EventResponse, EventWithArticle, EventListResponse

router = APIRouter()

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

@router.get("/events", response_model=EventListResponse)
async def list_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    country_iso: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size
    query = (
        select(Event, Article.title, Article.source_name, Article.source_url)
        .join(Article, Event.article_id == Article.article_id)
    )
    count_query = select(func.count(Event.event_id))

    if country_iso:
        query = query.where(Event.country_iso == country_iso.upper())
        count_query = count_query.where(Event.country_iso == country_iso.upper())

    if category:
        query = query.where(Event.category == category.upper())
        count_query = count_query.where(Event.category == category.upper())

    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0

    stmt = query.order_by(Event.timestamp.desc()).offset(offset).limit(page_size)
    res = await db.execute(stmt)

    events = []
    for ev, art_title, s_name, s_url in res.all():
        events.append(
            EventWithArticle(
                event_id=ev.event_id,
                article_id=ev.article_id,
                category=ev.category,
                country_iso=ev.country_iso,
                sentiment=ev.sentiment,
                severity=ev.severity,
                entities=ensure_list(ev.entities),
                timestamp=ev.timestamp,
                confidence=ev.confidence,
                model_version=ev.model_version,
                created_at=ev.created_at,
                article_title=art_title,
                source_name=s_name,
                source_url=s_url,
            )
        )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "events": events,
    }

@router.get("/events/{event_id}", response_model=EventWithArticle)
async def get_event(event_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Event, Article.title, Article.source_name, Article.source_url)
        .join(Article, Event.article_id == Article.article_id)
        .where(Event.event_id == event_id)
    )
    res = await db.execute(stmt)
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="Event not found")

    ev, art_title, s_name, s_url = row

    return EventWithArticle(
        event_id=ev.event_id,
        article_id=ev.article_id,
        category=ev.category,
        country_iso=ev.country_iso,
        sentiment=ev.sentiment,
        severity=ev.severity,
        entities=ensure_list(ev.entities),
        timestamp=ev.timestamp,
        confidence=ev.confidence,
        model_version=ev.model_version,
        created_at=ev.created_at,
        article_title=art_title,
        source_name=s_name,
        source_url=s_url,
    )

@router.get("/events/export/csv")
async def export_events_csv(
    country_iso: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(500, ge=1, le=5000),
    db: AsyncSession = Depends(get_db),
):
    """
    Exports structured geopolitical event telemetry as a downloadable CSV
    for offline statistical and intelligence spreadsheet workflows.
    """
    import io
    import csv
    from fastapi.responses import Response

    query = (
        select(Event, Article.title, Article.source_name, Article.source_url)
        .join(Article, Event.article_id == Article.article_id)
    )
    if country_iso:
        query = query.where(Event.country_iso == country_iso.upper())
    if category:
        query = query.where(Event.category == category.upper())

    stmt = query.order_by(Event.timestamp.desc()).limit(limit)
    res = await db.execute(stmt)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "event_id", "timestamp", "country_iso", "category",
        "sentiment", "severity", "confidence", "article_title",
        "source_name", "source_url", "model_version"
    ])

    for ev, title, s_name, s_url in res.all():
        writer.writerow([
            ev.event_id,
            ev.timestamp.isoformat() if ev.timestamp else "",
            ev.country_iso,
            ev.category,
            round(ev.sentiment, 3) if ev.sentiment is not None else "",
            round(ev.severity, 3) if ev.severity is not None else "",
            round(ev.confidence, 3) if ev.confidence is not None else "",
            title or "",
            s_name or "",
            s_url or "",
            ev.model_version or "",
        ])

    csv_bytes = output.getvalue()
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=geosentinel_events_{country_iso or 'all'}.csv"
        },
    )

