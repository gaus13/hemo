"""add uppercase cancelled volunteer status

Revision ID: c1f4a7e2b9d0
Revises: 48b62d3cc0ca
Create Date: 2026-08-19 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "c1f4a7e2b9d0"
down_revision: Union[str, Sequence[str], None] = "48b62d3cc0ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE volunteer_status ADD VALUE IF NOT EXISTS 'CANCELLED'")


def downgrade() -> None:
    # PostgreSQL does not directly support removing an enum value.
    pass
