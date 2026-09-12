
import httpx

from app.core.config import settings


TELEGRAM_API_URL = (
    f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"
)


def send_message(
    chat_id: int,
    text: str,
) -> None:
    url = f"{TELEGRAM_API_URL}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    response = httpx.post(
        url,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()


def send_photo(
    chat_id: int,
    photo_url: str,
    caption: str | None = None,
) -> None:
    url = f"{TELEGRAM_API_URL}/sendPhoto"

    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
    }

    if caption:
        payload["caption"] = caption

    response = httpx.post(
        url,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()
