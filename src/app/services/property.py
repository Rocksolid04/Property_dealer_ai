from sqlalchemy.orm import Session

from app.repositories.property import PropertyRepository
from app.schemas.property import PropertyCreate


class PropertyService:

    def __init__(self, db: Session):
        self.repository = PropertyRepository(db)

    def create_property(self,property_data: PropertyCreate,owner_id: int):
        return self.repository.create(property_data,owner_id)

    def get_property(self, property_id: int):
        return self.repository.get_by_id(property_id)

    def get_properties(self):
        return self.repository.get_all()

    def delete_property(self, property_id: int):
        property_obj = self.repository.get_by_id(property_id)

        if property_obj is None:
            return None

        self.repository.delete(property_obj)

        return property_obj

    def search_properties(
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
        return self.repository.search(
            location=location,
            property_type=property_type,
            listing_type=listing_type,
            min_price=min_price,
            max_price=max_price,
            bedrooms=bedrooms,
            page=page,
            limit=limit,
            sort_by=sort_by,
            order=order,
        )