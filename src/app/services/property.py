import json

from sqlalchemy.orm import Session

from app.database.redis import redis_client
from app.repositories.property import PropertyRepository
from app.schemas.property import (
    PropertyCreate,
    PropertyResponse,
    PropertySearchResponse,
)

from app.services.query_parser import parse_property_query
from app.services.embedding import generate_embedding

from app.models.properties import Property


class PropertyService:

    def __init__(self, db: Session):
        self.repository = PropertyRepository(db)

    def invalidate_property_search_cache(self):
        property_search_keys = redis_client.keys(
            "property_search:*"
        )

        ai_search_keys = redis_client.keys(
            "ai_search:*"
        )

        keys = property_search_keys + ai_search_keys

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
        current_user,
    ):
        property_obj = self.repository.get_by_id(
            property_id
        )

        if property_obj is None:
            return None

        if (
            current_user.role != "admin"
            and property_obj.owner_id != current_user.id
        ):
            raise PermissionError(
                "You can only delete your own properties"
            )

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
        owner_id=None,
        page=1,
        limit=10,
        sort_by="created_at",
        order="desc",
    ):
        cache_key = (
            f"property_search:{location}:"
            f"{property_type}:{listing_type}:"
            f"{min_price}:{max_price}:{bedrooms}:{owner_id}"
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
            owner_id=owner_id,
            page=page,
            limit=limit,
            sort_by=sort_by,
            order=order,
        )

        response = PropertySearchResponse.model_validate(result)
        result_data = response.model_dump(mode="json")

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
        page: int = 1,
        limit: int = 10,
    ):
        # Generate embedding for semantic search
        query_embedding = generate_embedding(query)

        # Send both keyword query and embedding
        # to the repository
        result = self.repository.hybrid_search(
            query=query,
            query_embedding=query_embedding,
            location=location,
            property_type=property_type,
            listing_type=listing_type,
            min_price=min_price,
            max_price=max_price,
            bedrooms=bedrooms,
            page=page,
            limit=limit,
        )

        # Repository returns:
        #
        # Property
        # distance
        # keyword_rank
        # hybrid_score
        #
        # So we unpack all 4 values.
        items = [
            {
                "property": property_obj,
                "vector_rank": vector_rank,
                "keyword_rank": keyword_rank,
                "rrf_score": rrf_score,
            }
            for (
                property_obj,
                vector_rank,
                keyword_rank,
                rrf_score,
            ) in result["items"]
        ]

        return {
            "items": items,
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"],
            "total_pages": result["total_pages"],
        }

    def ai_search(
        self,
        query: str,
        page: int = 1,
        limit: int = 10,
    ):
        normalized_query = " ".join(
            query.strip().lower().split()
        )

        cache_key = (
            f"ai_search:{normalized_query}:"
            f"{page}:{limit}"
        )

        cached_result = redis_client.get(cache_key)

        if cached_result:
            print("AI SEARCH CACHE HIT")
            return json.loads(cached_result)

        print("AI SEARCH CACHE MISS")

        parsed_query = parse_property_query(query)

        result = self.hybrid_search(
            query=parsed_query.search_text or query,
            location=parsed_query.location,
            property_type=parsed_query.property_type,
            listing_type=parsed_query.listing_type,
            min_price=parsed_query.min_price,
            max_price=parsed_query.max_price,
            bedrooms=parsed_query.bedrooms,
            page=page,
            limit=limit,
        )

        items = [
            {
                "property": PropertyResponse.model_validate(
                    item["property"]
                ).model_dump(mode="json"),
                "rrf_score": item["rrf_score"],
            }
            for item in result["items"]
        ]

        response = {
            "items": items,
            "filters": parsed_query.model_dump(),
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"],
            "total_pages": result["total_pages"],
        }

        redis_client.setex(
            cache_key,
            300,
            json.dumps(response),
        )

        return response

    def update_property(
        self,
        property_id: int,
        property_data: PropertyCreate,
        current_user,
    ):
        property_obj = self.repository.get_by_id(property_id)

        if property_obj is None:
            return None

        if (
            current_user.role != "admin"
            and property_obj.owner_id != current_user.id
        ):
            raise PermissionError(
                "You can only update your own properties"
            )

        updated_property = self.repository.update(
            property_obj,
            property_data,
        )

        self.invalidate_property_search_cache()

        return updated_property
    
    def update_property_owner(
        self,
        property_obj: Property,
        owner_id: int,
    ) -> Property:
        return self.repository.update_owner(
            property_obj,
            owner_id,
        )
        
    def get_property_stats(self):
        return self.repository.get_property_stats()