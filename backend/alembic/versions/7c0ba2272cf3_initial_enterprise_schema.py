"""initial_enterprise_schema

Revision ID: 7c0ba2272cf3
Revises: 
Create Date: 2026-11-13 12:58:04.187591

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c0ba2272cf3'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Table: articles
    op.create_table(
        'articles',
        sa.Column('article_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('source_name', sa.String(length=128), nullable=False, server_default='Unknown Source'),
        sa.Column('source_url', sa.Text(), nullable=False),
        sa.Column('credibility', sa.Float(), nullable=False, server_default='0.90'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('body_text', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=True, server_default='en'),
        sa.Column('author', sa.String(length=256), nullable=True),
        sa.Column('country_hint', sa.String(length=3), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=True, server_default='processed'),
        sa.Column('dedup_type', sa.String(length=32), nullable=True, server_default='unique'),
        sa.Column('canonical_article_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('article_id')
    )
    op.create_index(op.f('ix_articles_content_hash'), 'articles', ['content_hash'], unique=True)
    op.create_index(op.f('ix_articles_published_at'), 'articles', ['published_at'], unique=False)
    op.create_index(op.f('ix_articles_status'), 'articles', ['status'], unique=False)

    # 2. Table: events
    op.create_table(
        'events',
        sa.Column('event_id', sa.String(length=36), nullable=False),
        sa.Column('article_id', sa.String(length=36), nullable=False),
        sa.Column('category', sa.String(length=32), nullable=False),
        sa.Column('country_iso', sa.String(length=3), nullable=False),
        sa.Column('sentiment', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('severity', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('entities', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True, server_default='0.95'),
        sa.Column('model_version', sa.String(length=32), nullable=True, server_default='tfidf-logistic-v1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['article_id'], ['articles.article_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('event_id')
    )
    op.create_index(op.f('ix_events_article_id'), 'events', ['article_id'], unique=False)
    op.create_index(op.f('ix_events_category'), 'events', ['category'], unique=False)
    op.create_index(op.f('ix_events_country_iso'), 'events', ['country_iso'], unique=False)
    op.create_index(op.f('ix_events_timestamp'), 'events', ['timestamp'], unique=False)

    # 3. Table: country_scores
    op.create_table(
        'country_scores',
        sa.Column('score_id', sa.String(length=36), nullable=False),
        sa.Column('country_iso', sa.String(length=3), nullable=False),
        sa.Column('risk_index', sa.Float(), nullable=False),
        sa.Column('decayed_agg', sa.Float(), nullable=False),
        sa.Column('risk_tier', sa.String(length=16), nullable=False),
        sa.Column('event_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('contributing_factors', sa.JSON(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('score_id')
    )
    op.create_index(op.f('ix_country_scores_country_iso'), 'country_scores', ['country_iso'], unique=False)
    op.create_index(op.f('ix_country_scores_risk_tier'), 'country_scores', ['risk_tier'], unique=False)
    op.create_index(op.f('ix_country_scores_calculated_at'), 'country_scores', ['calculated_at'], unique=False)

    # 4. Table: summaries
    op.create_table(
        'summaries',
        sa.Column('summary_id', sa.String(length=36), nullable=False),
        sa.Column('country_iso', sa.String(length=3), nullable=False),
        sa.Column('bullet_points', sa.JSON(), nullable=False),
        sa.Column('evidence_links', sa.JSON(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('model_version', sa.String(length=32), nullable=True, server_default='extractive-heuristics-v1'),
        sa.PrimaryKeyConstraint('summary_id')
    )
    op.create_index(op.f('ix_summaries_country_iso'), 'summaries', ['country_iso'], unique=False)
    op.create_index(op.f('ix_summaries_generated_at'), 'summaries', ['generated_at'], unique=False)

    # 5. Table: alerts
    op.create_table(
        'alerts',
        sa.Column('alert_id', sa.String(length=36), nullable=False),
        sa.Column('country_iso', sa.String(length=3), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('trigger_tier', sa.String(length=16), nullable=False),
        sa.Column('trigger_reason', sa.String(length=64), nullable=True, server_default='critical_threshold'),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('alert_id')
    )
    op.create_index(op.f('ix_alerts_country_iso'), 'alerts', ['country_iso'], unique=False)
    op.create_index(op.f('ix_alerts_sent_at'), 'alerts', ['sent_at'], unique=False)

    # 6. Table: risk_score_history
    op.create_table(
        'risk_score_history',
        sa.Column('history_id', sa.String(length=36), nullable=False),
        sa.Column('country_iso', sa.String(length=3), nullable=False),
        sa.Column('risk_index', sa.Float(), nullable=False),
        sa.Column('risk_tier', sa.String(length=16), nullable=False),
        sa.Column('event_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('contributing_factors', sa.JSON(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('history_id')
    )
    op.create_index(op.f('ix_risk_score_history_country_iso'), 'risk_score_history', ['country_iso'], unique=False)
    op.create_index(op.f('ix_risk_score_history_recorded_at'), 'risk_score_history', ['recorded_at'], unique=False)


def downgrade() -> None:
    op.drop_table('risk_score_history')
    op.drop_table('alerts')
    op.drop_table('summaries')
    op.drop_table('country_scores')
    op.drop_table('events')
    op.drop_table('articles')
