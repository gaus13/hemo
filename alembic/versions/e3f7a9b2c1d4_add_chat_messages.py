"""add chat messages

Revision ID: e3f7a9b2c1d4
Revises: d2e5f8a1b7c9
Create Date: 2026-08-23 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e3f7a9b2c1d4"
down_revision: Union[str, Sequence[str], None] = "d2e5f8a1b7c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("sender_user_id", sa.Integer(), nullable=False),
        sa.Column("message_text", sa.Text(), nullable=False),
        sa.Column("client_message_id", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "char_length(message_text) BETWEEN 1 AND 2000",
            name="ck_chat_messages_message_text_length",
        ),
        sa.ForeignKeyConstraint(
            ["request_id"],
            ["blood_requests.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["sender_user_id"], ["users.id"]),
        sa.UniqueConstraint(
            "sender_user_id",
            "client_message_id",
            name="uq_chat_messages_sender_client_id",
        ),
    )
    op.create_index(
        "ix_chat_messages_id",
        "chat_messages",
        ["id"],
    )
    op.create_index(
        "ix_chat_messages_request_id",
        "chat_messages",
        ["request_id"],
    )
    op.create_index(
        "ix_chat_messages_sender_user_id",
        "chat_messages",
        ["sender_user_id"],
    )
    op.create_index(
        "ix_chat_messages_request_created_at",
        "chat_messages",
        ["request_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_chat_messages_request_created_at",
        table_name="chat_messages",
    )
    op.drop_index(
        "ix_chat_messages_sender_user_id",
        table_name="chat_messages",
    )
    op.drop_index("ix_chat_messages_request_id", table_name="chat_messages")
    op.drop_index("ix_chat_messages_id", table_name="chat_messages")
    op.drop_table("chat_messages")
