from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.models.event import Event
from app.models.article import Article
from app.schemas.event import EventResponse, EventWithArticle, EventListResponse

router = APIRouter()

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
                entities=ev.entities or [],
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
        entities=ev.entities or [],
        timestamp=ev.timestamp,
        confidence=ev.confidence,
        model_version=ev.model_version,
        created_at=ev.created_at,
        article_title=art_title,
        source_name=s_name,
        source_url=s_url,
    )
