
from sqlalchemy import select

from app.database.connection import SessionLocal
from app.models.properties import Property
from app.services.embedding import generate_embedding


def build_property_text(property: Property) -> str:
    parts = [
        property.title,
        property.description,
        property.property_type,
        property.listing_type,
        property.location,
    ]

    if property.bedrooms is not None:
        parts.append(f"{property.bedrooms} bedrooms")

    if property.bathrooms is not None:
        parts.append(f"{property.bathrooms} bathrooms")

    if property.area_sqft is not None:
        parts.append(f"{property.area_sqft} sqft")

    if property.price is not None:
        parts.append(f"price {property.price} rupees")

    return ". ".join(
        str(part)
        for part in parts
        if part
    )


def generate_property_embeddings():
    db = SessionLocal()

    try:
        properties = db.scalars(
            select(Property).where(
                Property.embedding.is_(None)
            )
        ).all()

        print(
            f"Found {len(properties)} properties "
            f"without embeddings."
        )

        for property in properties:
            property_text = build_property_text(property)

            embedding = generate_embedding(property_text)

            property.embedding = embedding

            print(
                f"Generated embedding for property "
                f"{property.id}: {property.title}"
            )

        db.commit()

        print(
            f"Successfully generated embeddings for "
            f"{len(properties)} properties."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    generate_property_embeddings()

