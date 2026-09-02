from sqlalchemy.orm import Session

from app.repositories.property_image import (
    delete_property_image as delete_image_record,
    get_property_image,
    get_property_images,
)
from app.services.storage import delete_property_image as delete_storage_image


def get_images_for_property(
    db: Session,
    property_id: int,
):
    return get_property_images(
        db=db,
        property_id=property_id,
    )


def delete_image(
    db: Session,
    property_id: int,
    image_id: int,
) -> bool:

    image = get_property_image(
        db=db,
        property_id=property_id,
        image_id=image_id,
    )

    if image is None:
        return False

    delete_storage_image(image.storage_path)

    delete_image_record(
        db=db,
        image=image,
    )

    return True