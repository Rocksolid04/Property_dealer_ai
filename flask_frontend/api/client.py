from typing import Any

import requests

from config import FASTAPI_URL


class APIError(Exception):
    """Raised when the FastAPI backend returns an error."""


def _request(
    method: str,
    endpoint: str,
    *,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> Any:
    url = f"{FASTAPI_URL}{endpoint}"

    try:
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json,
            headers=headers,
            timeout=60,
        )

    except requests.exceptions.ConnectionError as exc:
        raise APIError(
            f"Cannot connect to FastAPI at {url}. "
            "Make sure FastAPI is running on port 8000."
        ) from exc

    except requests.exceptions.Timeout as exc:
        raise APIError(
            f"FastAPI request timed out: {url}"
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise APIError(
            f"Request to FastAPI failed: {exc}"
        ) from exc

    if not response.ok:
        try:
            error_data = response.json()

            if isinstance(error_data, dict):
                detail = error_data.get(
                    "detail",
                    f"API request failed with status {response.status_code}",
                )
            else:
                detail = (
                    f"API request failed with status "
                    f"{response.status_code}"
                )

        except ValueError:
            detail = (
                f"API request failed with status "
                f"{response.status_code}: "
                f"{response.text[:300]}"
            )

        raise APIError(str(detail))

    if response.status_code == 204:
        return None

    try:
        return response.json()

    except ValueError as exc:
        raise APIError(
            "FastAPI returned an invalid JSON response."
        ) from exc


def get_properties() -> list[dict]:
    data = _request(
        "GET",
        "/properties/",
    )

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        return data.get("items", [])

    raise APIError(
        "Unexpected response format from /properties/."
    )


def get_property(property_id: int) -> dict:
    data = _request(
        "GET",
        f"/properties/{property_id}",
    )

    if not isinstance(data, dict):
        raise APIError(
            "Unexpected response format for property."
        )

    return data


def get_property_images(property_id: int) -> list[dict]:
    data = _request(
        "GET",
        f"/properties/{property_id}/images",
    )

    if isinstance(data, list):
        return data

    return []


def search_properties(
    *,
    location: str | None = None,
    property_type: str | None = None,
    listing_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    bedrooms: int | None = None,
    page: int = 1,
    limit: int = 10,
) -> dict:

    params = {
        "location": location,
        "property_type": property_type,
        "listing_type": listing_type,
        "min_price": min_price,
        "max_price": max_price,
        "bedrooms": bedrooms,
        "page": page,
        "limit": limit,
    }

    data = _request(
        "GET",
        "/properties/search",
        params=params,
    )

    if not isinstance(data, dict):
        raise APIError(
            "Unexpected response format from property search."
        )

    return data


def semantic_search(
    query: str,
    limit: int = 5,
) -> list[dict]:

    data = _request(
        "GET",
        "/properties/semantic-search",
        params={
            "query": query,
            "limit": limit,
        },
    )

    if not isinstance(data, list):
        raise APIError(
            "Unexpected response format from semantic search."
        )

    return data


def hybrid_search(
    query: str,
    *,
    location: str | None = None,
    property_type: str | None = None,
    listing_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    bedrooms: int | None = None,
    limit: int = 5,
) -> list[dict] | dict:

    params = {
        "query": query,
        "location": location,
        "property_type": property_type,
        "listing_type": listing_type,
        "min_price": min_price,
        "max_price": max_price,
        "bedrooms": bedrooms,
        "limit": limit,
    }

    return _request(
        "GET",
        "/properties/hybrid-search",
        params=params,
    )


def ai_search(
    query: str,
    *,
    page: int = 1,
    limit: int = 10,
) -> dict:

    data = _request(
        "GET",
        "/properties/ai-search",
        params={
            "query": query,
            "page": page,
            "limit": limit,
        },
    )

    if not isinstance(data, dict):
        raise APIError(
            "Unexpected response format from AI search."
        )

    return data

def register_user(
    name: str,
    email: str,
    password: str,
) -> dict:
    data = _request(
        "POST",
        "/users/",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )

    if not isinstance(data, dict):
        raise APIError(
            "Unexpected response format from user registration."
        )

    return data


def login_user(
    email: str,
    password: str,
) -> dict:
    data = _request(
        "POST",
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    if not isinstance(data, dict):
        raise APIError(
            "Unexpected response format from login."
        )

    return data


def get_current_user(
    token: str,
) -> dict:
    data = _request(
        "GET",
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    if not isinstance(data, dict):
        raise APIError(
            "Unexpected response format from current user."
        )

    return data
