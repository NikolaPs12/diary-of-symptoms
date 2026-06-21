"""add health scores

Revision ID: 8f2a7b31c9de
Revises: 03bd634fd8e4
Create Date: 2026-06-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f2a7b31c9de"
down_revision: Union[str, Sequence[str], None] = "03bd634fd8e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "health_scores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("calculated_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.CheckConstraint("score >= 1 AND score <= 100", name="check_score_range"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "calculated_at", name="uq_health_scores_user_day"),
    )
    op.create_index(op.f("ix_health_scores_id"), "health_scores", ["id"], unique=False)
    op.create_index(op.f("ix_health_scores_user_id"), "health_scores", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_health_scores_user_id"), table_name="health_scores")
    op.drop_index(op.f("ix_health_scores_id"), table_name="health_scores")
    op.drop_table("health_scores")
