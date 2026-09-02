from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.property import PropertyCreate, PropertyResponse, PropertySearchResponse
from app.services.property import PropertyService

from app.core.security import get_current_user, require_role
from app.models.user import User



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
    "/",
    response_model=list[PropertyResponse],
)
def get_properties(
    db: Session = Depends(get_db),
):
    service = PropertyService(db)

    return service.get_properties()


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