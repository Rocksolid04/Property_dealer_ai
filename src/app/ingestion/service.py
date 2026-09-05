
import requests

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ingestion.apify_client import fetch_properties
from app.ingestion.normalizer import normalize_property
from app.models.properties import Property
from app.models.property_image import PropertyImage
from app.services.storage import upload_property_image


def download_image(image_url: str) -> tuple[bytes, str]:
    """
    Download an image from the original source.

    Returns:
        tuple:
            - image content as bytes
            - content type such as image/jpeg
    """

    response = requests.get(
        image_url,
        timeout=15,
    )

    response.raise_for_status()

    content_type = response.headers.get(
        "Content-Type",
        "image/jpeg",
    )

    return response.content, content_type


def get_file_extension(content_type: str) -> str:
    """
    Convert a MIME type into a file extension.

    Examples:
        image/jpeg -> jpg
        image/png  -> png
        image/webp -> webp
    """

    extension = content_type.split("/")[-1].split(";")[0].lower()

    if extension == "jpeg":
        return "jpg"

    return extension


def ingest_properties(
    db: Session,
    city: str = "Mumbai",
    transaction_type: str = "buy",
    max_results: int = 10,
) -> int:
    """
    Fetch properties from Apify, normalize them,
    skip invalid/duplicate properties, download their images,
    upload images to Supabase Storage, and save image metadata
    in PostgreSQL.
    """

    # ---------------------------------------------------------
    # 1. Fetch raw properties from Apify
    # ---------------------------------------------------------

    raw_properties = fetch_properties(
        city=city,
        transaction_type=transaction_type,
        max_results=max_results,
    )

    inserted_count = 0

    # ---------------------------------------------------------
    # 2. Process each property
    # ---------------------------------------------------------

    for raw_property in raw_properties:

        # -----------------------------------------------------
        # Normalize property data
        # -----------------------------------------------------

        try:
            normalized_property = normalize_property(raw_property)

        except (ValueError, TypeError) as exc:
            print(f"Skipping invalid property: {exc}")
            continue

        external_id = normalized_property["external_id"]

        # -----------------------------------------------------
        # Skip duplicate property
        # -----------------------------------------------------

        if external_id:
            existing_property = db.scalar(
                select(Property).where(
                    Property.external_id == external_id
                )
            )

            if existing_property:
                print(
                    f"Skipping duplicate property: "
                    f"{external_id}"
                )
                continue

        # -----------------------------------------------------
        # Create property database record
        # -----------------------------------------------------

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

        print(
            f"Inserted property: "
            f"{property_record.id} - "
            f"{property_record.title}"
        )

        # -----------------------------------------------------
        # 3. Get scraped image URLs
        # -----------------------------------------------------

        images = raw_property.get(
            "propertyImages",
            [],
        )

        # -----------------------------------------------------
        # 4. Download and upload images
        # -----------------------------------------------------

        for display_order, image_url in enumerate(images):

            if not image_url:
                continue

            try:
                # Download image from 99acres
                image_content, content_type = download_image(
                    image_url
                )

                # Determine correct file extension
                extension = get_file_extension(
                    content_type
                )

                # Create deterministic storage path
                file_path = (
                    f"properties/"
                    f"{property_record.id}/"
                    f"image_{display_order}.{extension}"
                )

                # Upload image to Supabase Storage
                upload_result = upload_property_image(
                    file_content=image_content,
                    file_path=file_path,
                    content_type=content_type,
                )

                # -------------------------------------------------
                # 5. Save image metadata in PostgreSQL
                # -------------------------------------------------

                property_image = PropertyImage(
                    property_id=property_record.id,
                    image_url=upload_result["public_url"],
                    storage_path=upload_result["storage_path"],
                    display_order=display_order,
                )

                db.add(property_image)

                print(
                    f"  Uploaded image "
                    f"{display_order + 1}/{len(images)}"
                )

            except Exception as exc:
                print(
                    f"  Skipping image "
                    f"{display_order} "
                    f"for property "
                    f"{property_record.id}: "
                    f"{exc}"
                )

        inserted_count += 1

    # ---------------------------------------------------------
    # 6. Commit everything to PostgreSQL
    # ---------------------------------------------------------

    db.commit()

    print(
        f"Ingestion completed. "
        f"Inserted {inserted_count} properties."
    )

    return inserted_count
