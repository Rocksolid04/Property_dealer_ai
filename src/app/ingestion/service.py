from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ingestion.apify_client import fetch_properties
from app.ingestion.normalizer import normalize_property
from app.models.properties import Property
from app.models.property_image import PropertyImage


def ingest_properties(
    db: Session,
    city: str = "Mumbai",
    transaction_type: str = "buy",
    max_results: int = 10,
) -> int:
    """
    Fetch properties from Apify, normalize them,
    skip invalid/duplicate properties, and save
    valid properties and their images to PostgreSQL.
    """

    raw_properties = fetch_properties(
        city=city,
        transaction_type=transaction_type,
        max_results=max_results,
    )

    inserted_count = 0

    for raw_property in raw_properties:

        # Normalize property data
        try:
            normalized_property = normalize_property(raw_property)
        except (ValueError, TypeError) as exc:
            print(f"Skipping invalid property: {exc}")
            continue

        external_id = normalized_property["external_id"]

        # Skip property if it already exists
        if external_id:
            existing_property = db.scalar(
                select(Property).where(
                    Property.external_id == external_id
                )
            )

            if existing_property:
                continue

        # Create database record
        property_record = Property(
            external_id=external_id,
            title=normalized_property["title"],
            description=normalized_property["description"],
            property_type=normalized_property["property_type"],
            listing_type=normalized_property["listing_type"],
            location=normalized_property["location"],
            price=normalized_property["price"],
            bedrooms=normalized_property["bedrooms"],
            bathrooms=normalized_property["bathrooms"],
            area_sqft=normalized_property["area_sqft"],
            owner_id=None,
        )

        db.add(property_record)

        # Flush so PostgreSQL assigns the property ID
        db.flush()

        # Get images from the scraped property
        images = raw_property.get("propertyImages", [])

        # Save each image
        for display_order, image_url in enumerate(images):
            if not image_url:
                continue

            property_image = PropertyImage(
                property_id=property_record.id,
                image_url=image_url,
                storage_path="",
                display_order=display_order,
            )

            db.add(property_image)

        inserted_count += 1

    # Commit once after processing all properties
    db.commit()

    return inserted_count