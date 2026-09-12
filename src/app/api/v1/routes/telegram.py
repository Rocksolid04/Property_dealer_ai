
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.rag_service import RAGService
from app.services.telegram import send_message, send_photo


router = APIRouter(
    prefix="/telegram",
    tags=["Telegram"],
)


@router.post("/webhook")
def telegram_webhook(
    update: dict,
    db: Session = Depends(get_db),
):
    message = update.get("message")

    if not message:
        return {"ok": True}

    chat = message.get("chat")
    text = message.get("text")

    if not chat or not text:
        return {"ok": True}

    chat_id = chat.get("id")

    service = RAGService(db)

    answer, properties = service.ask_with_properties(
        query=text,
        limit=5,
    )

    # Send AI answer first
    send_message(
        chat_id=chat_id,
        text=answer,
    )

    # Send the first image of each retrieved property
    for property_obj in properties:

        if not property_obj.images:
            continue

        image = sorted(
            property_obj.images,
            key=lambda item: item.display_order,
        )[0]

        caption = (
            f"🏠 Property ID: {property_obj.id}\n"
            f"{property_obj.title}\n"
            f"📍 {property_obj.location}\n"
            f"💰 ₹{property_obj.price:,.0f}"
        )

        if property_obj.bedrooms is not None:
            caption += (
                f"\n🛏 {property_obj.bedrooms} BHK"
            )

        if property_obj.area_sqft is not None:
            caption += (
                f"\n📐 {property_obj.area_sqft:,.0f} sq ft"
            )

        send_photo(
            chat_id=chat_id,
            photo_url=image.image_url,
            caption=caption,
        )

    return {"ok": True}
