
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.security import require_role
from app.database.dependencies import get_db
from app.models.user import User
from app.repositories.property_image import create_property_image
from app.schemas.property import (
    PropertyCreate,
    PropertyImageResponse,
    PropertyResponse,
    PropertySearchResponse,
    PropertySemanticSearchResponse,
)
from app.services.property import PropertyService
from app.services.storage import upload_property_image
from app.services.property_image import get_images_for_property
from app.services.property_image import (
    delete_image,
    get_images_for_property,
)



router = APIRouter(
    prefix="/properties",
    tags=["Properties"],
)


@router.post(
    "/",
    response_model=PropertyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("dealer", "admin")
    ),
):
    service = PropertyService(db)

    return service.create_property(property_data,current_user.id)

@router.get(
    "/search",
    response_model=PropertySearchResponse,
)
def search_properties(
    location: str | None = None,
    property_type: str | None = None,
    listing_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    bedrooms: int | None = None,
    page: int = 1,
    limit: int = 10,
    sort_by: str = "created_at",
    order: str = "desc",
    db: Session = Depends(get_db),
):
    service = PropertyService(db)

    return service.search_properties(
        location=location,
        property_type=property_type,
        listing_type=listing_type,
        min_price=min_price,
        max_price=max_price,
        bedrooms=bedrooms,
        page=page,
        limit=limit,
        sort_by=sort_by,
        order=order,
    )

@router.get(
    "/semantic-search",
    response_model=list[PropertySemanticSearchResponse],
)
def semantic_search_properties(
    query: str,
    limit: int = 5,
    db: Session = Depends(get_db),
):
    service = PropertyService(db)

    return service.semantic_search(
        query=query,
        limit=limit,
    )

@router.get(
    "/hybrid-search",
    response_model=list[PropertySemanticSearchResponse],
)
def hybrid_search_properties(
    query: str,
    location: str | None = None,
    property_type: str | None = None,
    listing_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    bedrooms: int | None = None,
    limit: int = 5,
    db: Session = Depends(get_db),
):
    service = PropertyService(db)

    return service.hybrid_search(
        query=query,
        location=location,
        property_type=property_type,
        listing_type=listing_type,
        min_price=min_price,
        max_price=max_price,
        bedrooms=bedrooms,
        limit=limit,
    )

@router.get(
    "/",
    response_model=list[PropertyResponse],
)
def get_properties(
    db: Session = Depends(get_db),
):
    service = PropertyService(db)

    return service.get_properties()


@router.post(
    "/{property_id}/images",
    response_model=PropertyImageResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_property_image_endpoint(
    property_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("dealer", "admin")
    ),
):
    service = PropertyService(db)

    property_obj = service.get_property(property_id)

    if property_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    file_content = file.file.read()

    unique_filename = f"{uuid4()}_{file.filename}"

    storage_path = f"{property_id}/{unique_filename}"

    result = upload_property_image(
        file_content=file_content,
        file_path=storage_path,
        content_type=file.content_type or "application/octet-stream",
    )

    image = create_property_image(
        db=db,
        property_id=property_id,
        image_url=result["public_url"],
        storage_path=result["storage_path"],
    )

    return image

@router.get(
    "/{property_id}/images",
    response_model=list[PropertyImageResponse],
)
def get_property_images_endpoint(
    property_id: int,
    db: Session = Depends(get_db),
):
    images = get_images_for_property(
        db=db,
        property_id=property_id,
    )

    return images

@router.get(
    "/{property_id}",
    response_model=PropertyResponse,
)
def get_property(
    property_id: int,
    db: Session = Depends(get_db),
):
    service = PropertyService(db)

    property_obj = service.get_property(property_id)

    if property_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    return property_obj


@router.delete(
    "/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
):
    service = PropertyService(db)

    property_obj = service.delete_property(property_id)

    if property_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    return None

@router.delete(
    "/{property_id}/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_property_image_endpoint(
    property_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("dealer", "admin")
    ),
):
    success = delete_image(
        db=db,
        property_id=property_id,
        image_id=image_id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property image not found",
        )

    return None

