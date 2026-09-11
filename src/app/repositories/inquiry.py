from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inquiry import Inquiry


class InquiryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        property_id: int,
        message: str | None,
    ) -> Inquiry:
        inquiry = Inquiry(
            user_id=user_id,
            property_id=property_id,
            message=message,
            status="new",
        )

        self.db.add(inquiry)
        self.db.commit()
        self.db.refresh(inquiry)

        return inquiry

    def get_by_user_and_property(
        self,
        user_id: int,
        property_id: int,
    ) -> Inquiry | None:
        statement = select(Inquiry).where(
            Inquiry.user_id == user_id,
            Inquiry.property_id == property_id,
        )

        return self.db.scalar(statement)

    def get_by_user(
        self,
        user_id: int,
    ) -> list[Inquiry]:
        statement = (
            select(Inquiry)
            .where(Inquiry.user_id == user_id)
            .order_by(Inquiry.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def get_by_property_owner(
        self,
        owner_id: int,
    ) -> list[Inquiry]:
        statement = (
            select(Inquiry)
            .join(Inquiry.property)
            .where(
                Inquiry.property.has(owner_id=owner_id)
            )
            .order_by(Inquiry.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def get_all(self) -> list[Inquiry]:
        statement = (
            select(Inquiry)
            .order_by(Inquiry.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def update_status(
        self,
        inquiry: Inquiry,
        status: str,
    ) -> Inquiry:
        inquiry.status = status

        self.db.commit()
        self.db.refresh(inquiry)

        return inquiry