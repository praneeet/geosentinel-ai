from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.models.article import Article
from app.schemas.article import ArticleResponse, ArticleListResponse

router = APIRouter()

@router.get("/articles", response_model=ArticleListResponse)
async def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    country_iso: Optional[str] = None,
    dedup_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size
    query = select(Article)
    count_query = select(func.count(Article.article_id))

    if country_iso:
        query = query.where(Article.country_hint == country_iso.upper())
        count_query = count_query.where(Article.country_hint == country_iso.upper())

    if dedup_type:
        query = query.where(Article.dedup_type == dedup_type)
        count_query = count_query.where(Article.dedup_type == dedup_type)

    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0

    stmt = query.order_by(Article.published_at.desc()).offset(offset).limit(page_size)
    res = await db.execute(stmt)
    articles = res.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "articles": articles,
    }

@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Article).where(Article.article_id == article_id)
    res = await db.execute(stmt)
    art = res.scalars().first()
    if not art:
        raise HTTPException(status_code=404, detail="Article not found")
    return art
