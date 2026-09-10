"""standardize property types

Revision ID: 98ace3ee2506
Revises: a11f025dfe4a
Create Date: 2026-09-09 22:30:09.929783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98ace3ee2506'
down_revision: Union[str, Sequence[str], None] = 'a11f025dfe4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute(
        """
        UPDATE properties
        SET property_type = 'apartment'
        WHERE property_type IN (
            'Residential Apartment',
            'Apartment / Project',
            'apartment'
        )
        """
    )

    op.execute(
        """
        UPDATE properties
        SET property_type = 'land'
        WHERE property_type = 'Residential Land'
        """
    )

    op.execute(
        """
        UPDATE properties
        SET property_type = 'house'
        WHERE property_type = 'Independent House/Villa'
        """
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.execute(
        """
        UPDATE properties
        SET property_type = 'Residential Apartment'
        WHERE property_type = 'apartment'
        """
    )

    op.execute(
        """
        UPDATE properties
        SET property_type = 'Residential Land'
        WHERE property_type = 'land'
        """
    )

    op.execute(
        """
        UPDATE properties
        SET property_type = 'Independent House/Villa'
        WHERE property_type = 'house'
        """
    )
