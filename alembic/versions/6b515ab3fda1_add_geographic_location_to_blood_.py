"""add geographic location to blood requests

Revision ID: 6b515ab3fda1
Revises: a3783609aac7
Create Date: 2026-08-11 20:32:47.833417
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision: str = "6b515ab3fda1"
down_revision: Union[str, Sequence[str], None] = "a3783609aac7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "blood_requests",
        sa.Column(
            "location",
            geoalchemy2.types.Geography(
                geometry_type="POINT",
                srid=4326,
                dimension=2,
                from_text="ST_GeogFromText",
                name="geography",
            ),
            nullable=True,
        ),
    )



def downgrade() -> None:
    op.drop_column("blood_requests", "location")