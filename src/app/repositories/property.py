from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.properties import Property
from app.schemas.property import PropertyCreate


class PropertyRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, property_data: PropertyCreate) -> Property:
        property_obj = Property(
            **property_data.model_dump()
        )

        self.db.add(property_obj)
        self.db.commit()
        self.db.refresh(property_obj)

        return property_obj

    def get_by_id(self, property_id: int) -> Property | None:
        statement = select(Property).where(Property.id == property_id)

        return self.db.scalar(statement)

    def get_all(self) -> list[Property]:
        statement = select(Property)

        return list(self.db.scalars(statement).all())

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
    ) -> list[Property]:

        statement = select(Property)

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

        return list(self.db.scalars(statement).all())