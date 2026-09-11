from groq import Groq

from app.core.config import settings


client = Groq(
    api_key=settings.GROQ_API_KEY
)


MODEL_NAME = "qwen/qwen3.8-27b"


def generate_rag_answer(
    query: str,
    context: str,
) -> str:

    system_prompt = """
You are an AI property assistant for a property dealer.

Answer the user's question using ONLY the property
information provided in the context.

Rules:
- Do not invent property details.
- Do not invent prices, locations, amenities, or availability.
- If the context does not contain enough information,
  clearly say that the information is not available.
- Keep the answer helpful and concise.
- Mention property IDs when recommending properties.
"""

    user_prompt = f"""
User query:
{query}

Property context:
{context}

Answer the user's query based only on the property context.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content