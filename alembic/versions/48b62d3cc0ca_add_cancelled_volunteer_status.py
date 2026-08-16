"""add cancelled volunteer status

Revision ID: 48b62d3cc0ca
Revises: 6b515ab3fda1
Create Date: 2026-08-16 23:06:35.028948

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "48b62d3cc0ca"
down_revision: Union[str, Sequence[str], None] = "6b515ab3fda1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE volunteer_status ADD VALUE IF NOT EXISTS 'cancelled'"
    )


def downgrade() -> None:
    # PostgreSQL does not directly support removing an enum value.
    pass