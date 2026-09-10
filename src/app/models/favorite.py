from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.properties import Property

from app.database.base import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    property: Mapped["Property"] = relationship("Property")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "property_id",
            name="uq_user_property_favorite",
        ),
    )