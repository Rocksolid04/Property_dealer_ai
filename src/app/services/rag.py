from sqlalchemy.orm import Session

from app.services.qdrant_retrieval import retrieve_properties
from app.services.rag_context import build_rag_context


def retrieve_rag_context(
    db: Session,
    query: str,
    limit: int = 5,
) -> str:
    """
    Retrieve relevant properties from Qdrant
    and convert them into RAG context.
    """

    properties = retrieve_properties(
        db=db,
        query=query,
        limit=limit,
    )

    return build_rag_context(properties)