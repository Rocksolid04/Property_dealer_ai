import json

from sqlalchemy.orm import Session

from app.database.redis import redis_client
from app.repositories.property import PropertyRepository
from app.schemas.property import (
    PropertyCreate,
    PropertySearchResponse,
)


class PropertyService:

    def __init__(self, db: Session):
        self.repository = PropertyRepository(db)

    def invalidate_property_search_cache(self):
        keys = redis_client.keys("property_search:*")

        if keys:
            redis_client.delete(*keys)

            print(
                f"Invalidated {len(keys)} property search cache(s)"
            )

    def create_property(
    self,
    property_data: PropertyCreate,
    owner_id: int,
    ):
        property = self.repository.create(
           property_data,
           owner_id,
        )

        self.invalidate_property_search_cache()

        return property

    def get_property(self, property_id: int):
        return self.repository.get_by_id(property_id)

    def get_properties(self):
        return self.repository.get_all()

    def delete_property(self, property_id: int):
        property_obj = self.repository.get_by_id(property_id)

        if property_obj is None:
            return None

        self.repository.delete(property_obj)

        self.invalidate_property_search_cache()

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
        cache_key = (
            f"property_search:"
            f"{location}:"
            f"{property_type}:"
            f"{listing_type}:"
            f"{min_price}:"
            f"{max_price}:"
            f"{bedrooms}:"
            f"{page}:"
            f"{limit}:"
            f"{sort_by}:"
            f"{order}"
        )

        cached_result = redis_client.get(cache_key)

        if cached_result:
            print("CACHE HIT")
            return json.loads(cached_result)

        print("CACHE MISS")

        result = self.repository.search(
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

        response = PropertySearchResponse.model_validate(
            result
        )

        result_data = response.model_dump(mode="json")

        redis_client.setex(
            cache_key,
            300,
            json.dumps(result_data),
        )

        return result_data