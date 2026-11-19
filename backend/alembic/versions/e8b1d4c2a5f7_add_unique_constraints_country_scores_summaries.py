"""add_unique_constraints_country_scores_summaries

Revision ID: e8b1d4c2a5f7
Revises: 7c0ba2272cf3
Create Date: 2026-11-19 12:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'e8b1d4c2a5f7'
down_revision: Union[str, Sequence[str], None] = '7c0ba2272cf3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Clean up duplicate country_scores keeping the most recent calculated_at
    conn = op.get_bind()
    dialect = conn.dialect.name

    if dialect == "postgresql":
        conn.execute(sa.text("""
            DELETE FROM country_scores a USING country_scores b
            WHERE a.country_iso = b.country_iso
              AND a.calculated_at < b.calculated_at;
        """))
        conn.execute(sa.text("""
            DELETE FROM summaries a USING summaries b
            WHERE a.country_iso = b.country_iso
              AND a.generated_at < b.generated_at;
        """))
    else:
        # SQLite compatible deduplication
        conn.execute(sa.text("""
            DELETE FROM country_scores
            WHERE score_id NOT IN (
                SELECT score_id FROM (
                    SELECT score_id, MAX(calculated_at)
                    FROM country_scores
                    GROUP BY country_iso
                )
            );
        """))
        conn.execute(sa.text("""
            DELETE FROM summaries
            WHERE summary_id NOT IN (
                SELECT summary_id FROM (
                    SELECT summary_id, MAX(generated_at)
                    FROM summaries
                    GROUP BY country_iso
                )
            );
        """))

    # Drop existing non-unique indexes and create unique indexes
    with op.batch_alter_table('country_scores') as batch_op:
        batch_op.drop_index('ix_country_scores_country_iso')
        batch_op.create_index('ix_country_scores_country_iso', ['country_iso'], unique=True)

    with op.batch_alter_table('summaries') as batch_op:
        batch_op.drop_index('ix_summaries_country_iso')
        batch_op.create_index('ix_summaries_country_iso', ['country_iso'], unique=True)


def downgrade() -> None:
    with op.batch_alter_table('summaries') as batch_op:
        batch_op.drop_index('ix_summaries_country_iso')
        batch_op.create_index('ix_summaries_country_iso', ['country_iso'], unique=False)

    with op.batch_alter_table('country_scores') as batch_op:
        batch_op.drop_index('ix_country_scores_country_iso')
        batch_op.create_index('ix_country_scores_country_iso', ['country_iso'], unique=False)
