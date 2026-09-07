from groq import Groq

from app.core.config import settings


client = Groq(
    api_key=settings.GROQ_API_KEY
)


def parse_property_query(query: str):
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a real estate search assistant. "
                    "Understand the user's property search request "
                    "and extract the important requirements."
                ),
            },
            {
                "role": "user",
                "content": query,
            },
        ],
    )

    return response.choices[0].message.content