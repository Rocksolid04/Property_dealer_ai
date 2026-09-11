from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InquiryCreate(BaseModel):
    message: str | None = Field(
        default=None,
        max_length=1000,
    )


class InquiryStatusUpdate(BaseModel):
    status: str


class InquiryResponse(BaseModel):
    id: int
    user_id: int
    property_id: int
    message: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )