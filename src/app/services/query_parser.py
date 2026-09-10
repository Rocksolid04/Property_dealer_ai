from groq import Groq

from app.core.config import settings
from app.schemas.search import PropertySearchQuery


client = Groq(
    api_key=settings.GROQ_API_KEY
)


def parse_property_query(query: str) -> PropertySearchQuery:
    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a real estate search query parser. "
                        "Extract structured search filters from the user's request. "

                        "Return ONLY a JSON object matching this exact schema: "
                       "{"
                        '"location": "string or null", '
                        '"property_type": "apartment | house | land or null", '
                        '"listing_type": "buy | rent or null", '
                        '"min_price": "number or null", '
                        '"max_price": "number or null", '
                        '"bedrooms": "integer or null", '
                        '"search_text": "string or null"'
                        "}. "

                        "IMPORTANT: location MUST always be a plain string such as "
                        '"Mumbai", "Navi Mumbai", or "Thane". '
                        "Never return location as an object, dictionary, or nested JSON. "

                        "Return only information explicitly stated or strongly implied "
                        "by the user. "

                        "Convert Indian currency such as crore and lakh into INR. "
                        "For example, 2 crore means 20000000 and 50 lakh means 5000000. "

                        "For BHK, return only the bedroom number. "

                        "Normalize property type to one of: "
                        "'apartment', 'house', or 'land'. "

                        "For flats, apartments, BHKs, or residential apartments, "
                        "use 'apartment'. "

                        "For independent houses or villas, use 'house'. "

                        "For plots or residential land, use 'land'. "

                        "For listing type, use 'rent' when the user wants to rent, "
                        "and use 'buy' when the user wants to buy, purchase, or own "
                        "a property. "

                        "If the user explicitly says rent, rental, renting, monthly rent, or lease, use 'rent'."

                        "If the user explicitly says buy, buying, purchase, sale, or for sale, use 'buy'."

                        "If the user gives a property purchase-style budget using crore or lakh  "
                        "without mentioning rent, monthly rent, or lease, infer 'buy'."

                        "If neither rent nor buy can be reasonably inferred, return null for listing_type."

                        "Put qualitative requirements such as spacious, modern, "
                        "near metro, family-friendly, etc. into search_text. "

                        "If there are no qualitative requirements, return null "
                        "for search_text."
                    ),
                },
                {
                    "role": "user",
                    "content": query,
                },
            ],
            response_format={
                "type": "json_object"
            },
            max_tokens=200,
        )

        return PropertySearchQuery.model_validate_json(
            response.choices[0].message.content
        )

    except Exception as exc:
        raise ValueError(
            "Unable to understand the property search query"
        ) from exc

   