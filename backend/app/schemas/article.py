from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl

class ArticleBase(BaseModel):
    title: str
    source_name: str
    source_url: str
    published_at: datetime
    body_text: str
    language: str = "en"
    author: Optional[str] = None
    credibility: float = Field(0.90, ge=0.0, le=1.0)
    country_hint: Optional[str] = None

class ArticleCreate(ArticleBase):
    pass

class ArticleResponse(ArticleBase):
    article_id: str
    content_hash: str
    status: str
    dedup_type: str
    created_at: datetime
    model_config = {"from_attributes": True}

class ArticleListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    articles: List[ArticleResponse]
