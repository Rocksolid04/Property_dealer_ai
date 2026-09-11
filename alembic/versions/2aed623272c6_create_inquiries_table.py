"""create inquiries table

Revision ID: 2aed623272c6
Revises: 31790d82da90
Create Date: 2026-09-11 04:23:03.899513

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2aed623272c6'
down_revision: Union[str, Sequence[str], None] = '31790d82da90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "inquiries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["property_id"],
            ["properties.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "property_id",
            name="uq_user_property_inquiry",
        ),
    )

    op.create_index(
        op.f("ix_inquiries_property_id"),
        "inquiries",
        ["property_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_inquiries_user_id"),
        "inquiries",
        ["user_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_index(
        op.f("ix_inquiries_user_id"),
        table_name="inquiries",
    )

    op.drop_index(
        op.f("ix_inquiries_property_id"),
        table_name="inquiries",
    )

    op.drop_table("inquiries")
    # ### end Alembic commands ###
