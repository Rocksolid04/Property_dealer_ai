from sqlalchemy.orm import Session

from app.models.inquiry import Inquiry
from app.repositories.inquiry import InquiryRepository


class InquiryService:
    def __init__(self, db: Session):
        self.repository = InquiryRepository(db)

    def create_inquiry(
        self,
        user_id: int,
        property_id: int,
        message: str | None,
    ) -> Inquiry:
        existing = self.repository.get_by_user_and_property(
            user_id,
            property_id,
        )

        if existing is not None:
            raise ValueError(
                "You have already submitted an inquiry for this property"
            )

        return self.repository.create(
            user_id,
            property_id,
            message,
        )

    def get_user_inquiries(
        self,
        user_id: int,
    ) -> list[Inquiry]:
        return self.repository.get_by_user(user_id)

    def get_dealer_inquiries(
        self,
        owner_id: int,
    ) -> list[Inquiry]:
        return self.repository.get_by_property_owner(owner_id)

    def get_all_inquiries(self) -> list[Inquiry]:
        return self.repository.get_all()

    def update_status(
        self,
        inquiry: Inquiry,
        status: str,
    ) -> Inquiry:
        allowed_statuses = {
            "new",
            "contacted",
            "interested",
            "closed",
        }

        if status not in allowed_statuses:
            raise ValueError(
                "Invalid inquiry status"
            )

        return self.repository.update_status(
            inquiry,
            status,
        )