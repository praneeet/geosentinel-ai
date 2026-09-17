from app.ingestion.base import BaseNewsSource
from app.ingestion.normalizer import sanitize_and_normalize_article
from app.ingestion.newsapi import NewsAPIClient
from app.ingestion.mediastack import MediaStackClient
from app.ingestion.rss import RSSClient
from app.ingestion.gdelt import GDELTClient
from app.ingestion.demo_source import DemoSource
from app.ingestion.service import IngestionService, ingestion_service

__all__ = [
    "BaseNewsSource",
    "sanitize_and_normalize_article",
    "NewsAPIClient",
    "MediaStackClient",
    "RSSClient",
    "GDELTClient",
    "DemoSource",
    "IngestionService",
    "ingestion_service",
]
