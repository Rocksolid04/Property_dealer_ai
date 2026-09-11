from math import ceil

from sqlalchemy import func, select, or_
from sqlalchemy.orm import Session, selectinload

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
        statement = (
        select(Property)
        .options(selectinload(Property.images))
        .where(Property.id == property_id)
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

    def update(
        self,
        property_obj: Property,
        property_data: PropertyCreate,
    ) -> Property:

        property_obj.title = property_data.title
        property_obj.description = property_data.description
        property_obj.property_type = property_data.property_type
        property_obj.listing_type = property_data.listing_type
        property_obj.location = property_data.location
        property_obj.price = property_data.price
        property_obj.bedrooms = property_data.bedrooms
        property_obj.bathrooms = property_data.bathrooms
        property_obj.area_sqft = property_data.area_sqft

        self.db.commit()
        self.db.refresh(property_obj)

        return property_obj
    
    def update_owner(
        self,
        property_obj: Property,
        owner_id: int,
    ) -> Property:
        property_obj.owner_id = owner_id

        self.db.commit()
        self.db.refresh(property_obj)

        return property_obj

    def search(
        self,
        location: str | None = None,
        property_type: str | None = None,
        listing_type: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        bedrooms: int | None = None,
        owner_id: int | None = None,
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
        if owner_id is not None:
            statement = statement.where(
                Property.owner_id == owner_id
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

    def vector_search(
        self,
        query_embedding: list[float],
        limit: int = 5,
    ):
        distance = Property.embedding.cosine_distance(
           query_embedding
    )

        statement = (
            select(
               Property,
               distance.label("distance"),
            )
            .where(Property.embedding.is_not(None))
            .order_by(distance)
            .limit(limit)
        )

        return self.db.execute(statement).all()

    def keyword_search(
        self,
        query: str,
        limit: int = 10,
    ):
        search_vector = (
            func.to_tsvector(
                "english",
               func.coalesce(Property.title, "")
               + " "
               + func.coalesce(Property.description, "")
               + " "
               + func.coalesce(Property.location, ""),
            )
        )

        search_query = func.plainto_tsquery(
            "english",
            query,
        )

        rank = func.ts_rank(
            search_vector,
            search_query,
        )

        statement = (
            select(
               Property,
               rank.label("rank"),
            )
            .where(
                search_vector.op("@@")(search_query)
            )
            .order_by(
               rank.desc()
            )
            .limit(limit)
        )

        return self.db.execute(statement).all()


    def hybrid_search(
        self,
        query: str,
        query_embedding: list[float],
        location: str | None = None,
        property_type: str | None = None,
        listing_type: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        bedrooms: int | None = None,
        page: int = 1,
        limit: int = 10,
    ):
        # --------------------------------
        # 1. RRF configuration
        # --------------------------------
        rrf_k = 60
        retrieval_limit = 50

        # --------------------------------
        # 2. Base filters
        # --------------------------------
        filters = []

        if location:
            normalized_location = location.strip().lower()

            filters.append(
                or_(
                    func.lower(Property.location)
                    == normalized_location,
                    func.lower(Property.location).like(
                        f"%, {normalized_location}"
                    ),
                )
            )

        if property_type:
            filters.append(
                Property.property_type == property_type
            )

        if listing_type:
            filters.append(
                Property.listing_type == listing_type
            )

        if min_price is not None:
            filters.append(
                Property.price >= min_price
            )

        if max_price is not None:
            filters.append(
                Property.price <= max_price
            )

        if bedrooms is not None:
            filters.append(
                Property.bedrooms == bedrooms
            )

        # --------------------------------
        # 3. Vector ranking
        # --------------------------------
        distance = Property.embedding.cosine_distance(
            query_embedding
        )

        vector_statement = (
            select(Property)
            .where(
                Property.embedding.is_not(None),
                *filters,
            )
            .order_by(distance)
            .limit(retrieval_limit)
        )

        vector_results = self.db.scalars(
            vector_statement
        ).all()

        #  --------------------------------
        # 4. Keyword ranking
        # --------------------------------
        search_vector = (
            func.to_tsvector(
                "english",
                func.coalesce(Property.title, "")
                + " "
                + func.coalesce(Property.description, "")
                + " "
                + func.coalesce(Property.location, ""),
            )
        )

        search_query = func.plainto_tsquery(
            "english",
            query,
        )

        keyword_rank = func.ts_rank(
            search_vector,
            search_query,
        )

        keyword_statement = (
            select(Property)
            .where(
                search_vector.op("@@")(search_query),
                *filters,
            )
            .order_by(keyword_rank.desc())
            .limit(retrieval_limit)
        )

        keyword_results = self.db.scalars(
            keyword_statement
        ).all()

        # --------------------------------
        # 5. Build RRF scores
        # --------------------------------
        rrf_scores = {}

        vector_ranks = {}

        for rank, property_obj in enumerate(
            vector_results,
            start=1,
        ):
            vector_ranks[property_obj.id] = rank

            rrf_scores[property_obj.id] = (
                rrf_scores.get(property_obj.id, 0)
                + 1 / (rrf_k + rank)
            )

        keyword_ranks = {}

        for rank, property_obj in enumerate(
            keyword_results,
            start=1,
        ):
            keyword_ranks[property_obj.id] = rank

            rrf_scores[property_obj.id] = (
                rrf_scores.get(property_obj.id, 0)
                + 1 / (rrf_k + rank)
            )

        # --------------------------------
        #    6. Create property lookup
        # --------------------------------
        properties = {
            property_obj.id: property_obj
            for property_obj in (
                vector_results + keyword_results
            )
        }

        # --------------------------------
        # 7. Sort by RRF score
        # --------------------------------
        ranked_results = sorted(
            rrf_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        # --------------------------------
        # 8. Pagination
        # --------------------------------
        
        count_statement = (
           select(func.count())
            .select_from(Property)
            .where(
            Property.embedding.is_not(None),
            *filters,
            )
        )

        total = self.db.scalar(count_statement) or 0

        offset = (page - 1) * limit

        paginated_results = ranked_results[
            offset: offset + limit
        ]

        items = []

        for property_id, rrf_score in paginated_results:
            property_obj = properties[property_id]

            items.append(
                (
                    property_obj,
                    vector_ranks.get(property_id),
                    keyword_ranks.get(property_id),
                    rrf_score,
                )
            )

        total_pages = (
            ceil(total / limit)
            if limit
            else 0
        )

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
        }
        
    def get_property_stats(self):
        total = self.db.query(Property).count()

        assigned = (
            self.db.query(Property)
            .filter(Property.owner_id.is_not(None))
            .count()
        )

        unassigned = (
            self.db.query(Property)
            .filter(Property.owner_id.is_(None))
            .count()
        )

        return {
            "total": total,
            "assigned": assigned,
            "unassigned": unassigned,
        }
        