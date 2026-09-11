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

    extension = (
        content_type
        .split("/")[-1]
        .split(";")[0]
        .lower()
    )

    if extension == "jpeg":
        return "jpg"

    return extension


def ingest_properties(
    db: Session,
    city: str = "Mumbai",
    transaction_type: str = "buy",
    max_results: int = 10,
    owner_id: int | None = None,
) -> int:
    """
    Fetch properties from Apify, normalize them,
    create new properties or update existing properties,
    download their images, upload images to Supabase Storage,
    and save image metadata in PostgreSQL.

    Returns:
        Number of newly inserted properties.
    """

    raw_properties = fetch_properties(
        city=city,
        transaction_type=transaction_type,
        max_results=max_results,
    )

    inserted_count = 0
    updated_count = 0
    skipped_count = 0

    for raw_property in raw_properties:

        # ---------------------------------------------------------
        # 1. Normalize property
        # ---------------------------------------------------------

        try:
            normalized_property = normalize_property(
                raw_property
            )

        except (ValueError, TypeError) as exc:
            print(
                f"Skipping invalid property: {exc}"
            )
            skipped_count += 1
            continue

        external_id = normalized_property.get(
            "external_id"
        )

        if not external_id:
            print(
                "Skipping property without external_id"
            )
            skipped_count += 1
            continue

        # ---------------------------------------------------------
        # 2. Check whether property already exists
        # ---------------------------------------------------------

        existing_property = db.scalar(
            select(Property).where(
                Property.external_id == external_id
            )
        )

        # ---------------------------------------------------------
        # 3. Update existing property
        # ---------------------------------------------------------

        if existing_property:

            existing_property.title = normalized_property[
                "title"
            ]

            existing_property.description = normalized_property[
                "description"
            ]

            existing_property.property_type = normalized_property[
                "property_type"
            ]

            existing_property.listing_type = normalized_property[
                "listing_type"
            ]

            existing_property.location = normalized_property[
                "location"
            ]

            existing_property.price = normalized_property[
                "price"
            ]

            existing_property.bedrooms = normalized_property[
                "bedrooms"
            ]

            existing_property.bathrooms = normalized_property[
                "bathrooms"
            ]

            existing_property.area_sqft = normalized_property[
                "area_sqft"
            ]

            # Only assign an owner when one was explicitly provided.
            # This prevents ingestion from accidentally changing
            # an already assigned property back to NULL.
            if owner_id is not None:
                existing_property.owner_id = owner_id

            updated_count += 1

            print(
                f"Updated property: "
                f"{existing_property.id} - "
                f"{existing_property.title}"
            )

            continue

        # ---------------------------------------------------------
        # 4. Create new property
        # ---------------------------------------------------------

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
            owner_id=owner_id,
        )

        try:
            db.add(property_record)

            # Get PostgreSQL-generated ID.
            db.flush()

        except Exception as exc:
            db.rollback()

            print(
                f"Skipping property "
                f"{external_id}: {exc}"
            )

            skipped_count += 1
            continue

        print(
            f"Inserted property: "
            f"{property_record.id} - "
            f"{property_record.title}"
        )

        # ---------------------------------------------------------
        # 5. Get scraped image URLs
        # ---------------------------------------------------------

        images = raw_property.get(
            "propertyImages",
            [],
        )

        if not isinstance(images, list):
            images = []

        # ---------------------------------------------------------
        # 6. Download and upload images
        # ---------------------------------------------------------

        for display_order, image_url in enumerate(images):

            if not image_url:
                continue

            try:
                image_content, content_type = (
                    download_image(image_url)
                )

                extension = get_file_extension(
                    content_type
                )

                file_path = (
                    f"properties/"
                    f"{property_record.id}/"
                    f"image_{display_order}.{extension}"
                )

                upload_result = upload_property_image(
                    file_content=image_content,
                    file_path=file_path,
                    content_type=content_type,
                )

                property_image = PropertyImage(
                    property_id=property_record.id,
                    image_url=upload_result[
                        "public_url"
                    ],
                    storage_path=upload_result[
                        "storage_path"
                    ],
                    display_order=display_order,
                )

                db.add(property_image)

                print(
                    f"  Uploaded image "
                    f"{display_order + 1}/{len(images)}"
                )

            except (
                requests.RequestException,
                ValueError,
                TypeError,
                Exception,
            ) as exc:
                print(
                    f"  Skipping image "
                    f"{display_order} "
                    f"for property "
                    f"{property_record.id}: "
                    f"{exc}"
                )

        inserted_count += 1

    # -------------------------------------------------------------
    # 7. Commit database changes
    # -------------------------------------------------------------

    try:
        db.commit()

    except Exception as exc:
        db.rollback()

        print(
            f"Ingestion database commit failed: {exc}"
        )

        raise

    # -------------------------------------------------------------
    # 8. Summary
    # -------------------------------------------------------------

    print(
        f"Ingestion completed. "
        f"Inserted: {inserted_count}, "
        f"Updated: {updated_count}, "
        f"Skipped: {skipped_count}"
    )

    return inserted_count