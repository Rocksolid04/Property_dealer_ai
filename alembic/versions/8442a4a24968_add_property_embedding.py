
"""add property embedding

Revision ID: 8442a4a24968
Revises: fa6f07bc1fc5
Create Date: 2026-09-06 03:48:14.156806

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy


# revision identifiers, used by Alembic.
revision: str = "8442a4a24968"
down_revision: Union[str, Sequence[str], None] = "fa6f07bc1fc5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "properties",
        sa.Column(
            "embedding",
            pgvector.sqlalchemy.vector.VECTOR(dim=384),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "properties",
        "embedding",
    )
