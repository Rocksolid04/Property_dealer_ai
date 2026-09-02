from math import ceil

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.properties import Property
from app.schemas.property import PropertyCreate


class PropertyRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self,property_data: PropertyCreate,owner_id: int,) -> Property:
        property_obj = Property(**property_data.model_dump(),owner_id=owner_id)

        self.db.add(property_obj)
        self.db.commit()
        self.db.refresh(property_obj)

        return property_obj

    def get_by_id(self, property_id: int) -> Property | None:
        statement = select(Property).where(
            Property.id == property_id
        )

        return self.db.scalar(statement)

    def get_all(self) -> list[Property]:
        statement = select(Property)

        return list(
            self.db.scalars(statement).all()
        )

    def delete(self, property_obj: Property) -> None:
        self.db.delete(property_obj)
        self.db.commit()

    def search(
        self,
        location: str | None = None,
        property_type: str | None = None,
        listing_type: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        bedrooms: int | None = None,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "created_at",
        order: str = "desc",
    ):
        statement = select(Property)

        # Filters
        if location:
            statement = statement.where(
                Property.location.ilike(f"%{location}%")
            )

        if property_type:
            statement = statement.where(
                Property.property_type == property_type
            )

        if listing_type:
            statement = statement.where(
                Property.listing_type == listing_type
            )

        if min_price is not None:
            statement = statement.where(
                Property.price >= min_price
            )

        if max_price is not None:
            statement = statement.where(
                Property.price <= max_price
            )

        if bedrooms is not None:
            statement = statement.where(
                Property.bedrooms == bedrooms
            )

        # Count total matching properties
        count_statement = select(
            func.count()
        ).select_from(statement.subquery())

        total = self.db.scalar(count_statement) or 0

        # Sorting
        sort_column = getattr(
            Property,
            sort_by,
            Property.created_at,
        )

        if order.lower() == "asc":
            statement = statement.order_by(sort_column.asc())
        else:
            statement = statement.order_by(sort_column.desc())

        # Pagination
        offset = (page - 1) * limit

        statement = statement.offset(offset).limit(limit)

        properties = list(
            self.db.scalars(statement).all()
        )

        total_pages = ceil(total / limit) if limit else 0

        return {
            "items": properties,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
        }