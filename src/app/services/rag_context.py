from app.models.properties import Property
from app.services.property_document import build_property_document


def build_rag_context(
    properties: list[Property],
) -> str:
    """
    Convert retrieved properties into context
    for the RAG LLM.
    """

    if not properties:
        return "No matching properties were found."

    context_parts = []

    for property_obj in properties:
        document = build_property_document(
            property_obj
        )

        context_parts.append(
            f"Property ID: {property_obj.id}\n"
            f"{document}"
        )

    return "\n\n---\n\n".join(context_parts)