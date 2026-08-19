"""add notifications

Revision ID: d2e5f8a1b7c9
Revises: c1f4a7e2b9d0
Create Date: 2026-08-19 12:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d2e5f8a1b7c9"
down_revision: Union[str, Sequence[str], None] = "c1f4a7e2b9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.String(length=36), nullable=False),
        sa.Column("recipient_user_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column(
            "is_read", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["recipient_user_id"], ["users.id"]),
        sa.UniqueConstraint("event_id"),
    )
    op.create_index("ix_notifications_id", "notifications", ["id"])
    op.create_index("ix_notifications_event_id", "notifications", ["event_id"])


def downgrade() -> None:
    op.drop_index("ix_notifications_event_id", table_name="notifications")
    op.drop_index("ix_notifications_id", table_name="notifications")
    op.drop_table("notifications")
