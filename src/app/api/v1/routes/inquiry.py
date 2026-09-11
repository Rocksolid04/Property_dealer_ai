from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_role
from app.database.dependencies import get_db
from app.models.properties import Property
from app.models.inquiry import Inquiry
from app.models.user import User
from app.schemas.inquiry import (
    InquiryCreate,
    InquiryResponse,
    InquiryStatusUpdate,
)
from app.services.inquiry import InquiryService


router = APIRouter(
    prefix="/inquiries",
    tags=["Inquiries"],
)


@router.post(
    "/",
    response_model=InquiryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_inquiry(
    inquiry_data: InquiryCreate,
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    property_obj = db.get(Property, property_id)

    if property_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    service = InquiryService(db)

    try:
        return service.create_inquiry(
            user_id=current_user.id,
            property_id=property_id,
            message=inquiry_data.message,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.get(
    "/me",
    response_model=list[InquiryResponse],
)
def get_my_inquiries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = InquiryService(db)

    return service.get_user_inquiries(
        current_user.id
    )


@router.get(
    "/dealer",
    response_model=list[InquiryResponse],
)
def get_dealer_inquiries(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("dealer", "admin")
    ),
):
    service = InquiryService(db)

    if current_user.role == "admin":
        return service.get_all_inquiries()

    return service.get_dealer_inquiries(
        current_user.id
    )


@router.patch(
    "/{inquiry_id}/status",
    response_model=InquiryResponse,
)
def update_inquiry_status(
    inquiry_id: int,
    inquiry_data: InquiryStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("dealer", "admin")
    ),
):
    inquiry = db.get(Inquiry, inquiry_id)

    if inquiry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inquiry not found",
        )

    if current_user.role == "dealer":
        property_obj = db.get(
            Property,
            inquiry.property_id,
        )

        if (
            property_obj is None
            or property_obj.owner_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this inquiry",
            )

    service = InquiryService(db)

    try:
        return service.update_status(
            inquiry,
            inquiry_data.status,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )