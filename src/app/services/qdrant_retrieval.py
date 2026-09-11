from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.properties import Property
from app.services.qdrant import search_properties


def retrieve_properties(
    db: Session,
    query: str,
    limit: int = 5,
) -> list[Property]:

    results = search_properties(
        query=query,
        limit=limit,
    )

    property_ids = [
        point.payload["property_id"]
        for point in results
        if point.payload
        and "property_id" in point.payload
    ]

    if not property_ids:
        return []

    properties = db.scalars(
        select(Property).where(
            Property.id.in_(property_ids)
        )
    ).all()

    property_map = {
        property_obj.id: property_obj
        for property_obj in properties
    }

    return [
        property_map[property_id]
        for property_id in property_ids
        if property_id in property_map
    ]