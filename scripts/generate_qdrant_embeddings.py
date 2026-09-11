from sqlalchemy import select

from app.database.connection import SessionLocal
from app.models.properties import Property
from app.services.property_document import build_property_document
from app.services.qdrant import (
    create_collection,
    upsert_property,
)


def main():
    create_collection()

    db = SessionLocal()

    try:
        properties = db.scalars(
            select(Property)
        ).all()

        for property_obj in properties:
            document = build_property_document(
                property_obj
            )

            upsert_property(
                property_id=property_obj.id,
                text=document,
            )

        print(
            f"Indexed {len(properties)} properties into Qdrant"
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()