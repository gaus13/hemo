"""add donor geographic location

Revision ID: a3783609aac7
Revises: 834fbc226987
Create Date: 2026-08-11 15:38:03.455191
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2


revision: str = "a3783609aac7"
down_revision: Union[str, Sequence[str], None] = "834fbc226987"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "donor_profiles",
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

    # # deleted this, due toGeoAlchemy2 is automatically creating the GiST spatial index  op.create_index(
    # "idx_donor_profiles_location",
    # "donor_profiles",
    # ["location"],
    # unique=False,
    # postgresql_using="gist",


    op.drop_column("donor_profiles", "latitude")
    op.drop_column("donor_profiles", "longitude")


def downgrade() -> None:
    op.add_column(
        "donor_profiles",
        sa.Column(
            "latitude",
            sa.Float(),
            nullable=True,
        ),
    )

    op.add_column(
        "donor_profiles",
        sa.Column(
            "longitude",
            sa.Float(),
            nullable=True,
        ),
    )

    op.drop_index(
        "idx_donor_profiles_location",
        table_name="donor_profiles",
        postgresql_using="gist",
    )

    op.drop_column("donor_profiles", "location")