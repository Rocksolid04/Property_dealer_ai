"""standardize sale listing type

Revision ID: a11f025dfe4a
Revises: 8442a4a24968
Create Date: 2026-09-07 22:29:15.434545

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a11f025dfe4a'
down_revision: Union[str, Sequence[str], None] = '8442a4a24968'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE properties
        SET listing_type = 'buy'
        WHERE listing_type = 'sale'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE properties
        SET listing_type = 'sale'
        WHERE listing_type = 'buy'
        """
    )
