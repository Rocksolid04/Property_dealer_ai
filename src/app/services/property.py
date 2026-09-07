import json

from sqlalchemy.orm import Session

from app.database.redis import redis_client
from app.repositories.property import PropertyRepository
from app.schemas.property import (
    PropertyCreate,
    PropertySearchResponse,
)
from app.services.embedding import generate_embedding


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

    def get_property(
        self,
        property_id: int,
    ):
        return self.repository.get_by_id(property_id)

    def get_properties(self):
        return self.repository.get_all()

    def delete_property(
        self,
        property_id: int,
    ):
        property_obj = self.repository.get_by_id(
            property_id
        )

        if property_obj is None:
            return None

        self.repository.delete(property_obj)

        self.invalidate_property_search_cache()

        return property_obj

    def search_properties(
        self,
        location=None,
        property_type=None,
        listing_type=None,
        min_price=None,
        max_price=None,
        bedrooms=None,
        page=1,
        limit=10,
        sort_by="created_at",
        order="desc",
    ):
        cache_key = (
            f"property_search:{location}:"
            f"{property_type}:{listing_type}:"
            f"{min_price}:{max_price}:{bedrooms}:"
            f"{page}:{limit}:{sort_by}:{order}"
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

        result_data = response.model_dump(
            mode="json"
        )

        redis_client.setex(
            cache_key,
            300,
            json.dumps(result_data),
        )

        return result_data

    def semantic_search(
        self,
        query: str,
        limit: int = 5,
    ):
        query_embedding = generate_embedding(query)

        results = self.repository.vector_search(
            query_embedding=query_embedding,
            limit=limit,
        )

        return [
            {
                "property": property_obj,
                "similarity": 1 - distance,
            }
            for property_obj, distance in results
        ]

    def hybrid_search(
        self,
        query: str,
        location: str | None = None,
        property_type: str | None = None,
        listing_type: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        bedrooms: int | None = None,
        limit: int = 5,
    ):
        query_embedding = generate_embedding(query)

        results = self.repository.hybrid_search(
            query_embedding=query_embedding,
            location=location,
            property_type=property_type,
            listing_type=listing_type,
            min_price=min_price,
            max_price=max_price,
            bedrooms=bedrooms,
            limit=limit,
        )

        return [
            {
                "property": property_obj,
                "similarity": 1 - distance,
            }
            for property_obj, distance in results
        ]