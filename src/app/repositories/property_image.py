from sqlalchemy.orm import Session

from app.models.property_image import PropertyImage


def create_property_image(
    db: Session,
    property_id: int,
    image_url: str,
    storage_path: str,
    display_order: int = 0,
) -> PropertyImage:

    image = PropertyImage(
        property_id=property_id,
        image_url=image_url,
        storage_path=storage_path,
        display_order=display_order,
    )

    db.add(image)
    db.commit()
    db.refresh(image)

    return image

def get_property_images(
    db: Session,
    property_id: int,
) -> list[PropertyImage]:

    return (
        db.query(PropertyImage)
        .filter(PropertyImage.property_id == property_id)
        .order_by(PropertyImage.display_order)
        .all()
    )

def get_property_image(
    db: Session,
    property_id: int,
    image_id: int,
) -> PropertyImage | None:

    return (
        db.query(PropertyImage)
        .filter(
            PropertyImage.id == image_id,
            PropertyImage.property_id == property_id,
        )
        .first()
    )

def delete_property_image(
    db: Session,
    image: PropertyImage,
) -> None:

    db.delete(image)
    db.commit()