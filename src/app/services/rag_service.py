
from sqlalchemy.orm import Session

from app.models.properties import Property
from app.services.rag_context import build_rag_context
from app.services.rag_generation import generate_rag_answer
from app.services.qdrant_retrieval import retrieve_properties


class RAGService:
    def __init__(self, db: Session):
        self.db = db

    def ask_with_properties(
        self,
        query: str,
        limit: int = 5,
    ) -> tuple[str, list[Property]]:

        properties = retrieve_properties(
            db=self.db,
            query=query,
            limit=limit,
        )

        context = build_rag_context(
            properties
        )

        answer = generate_rag_answer(
            query=query,
            context=context,
        )

        return answer, properties

    def ask(
        self,
        query: str,
        limit: int = 5,
    ) -> str:

        answer, _ = self.ask_with_properties(
            query=query,
            limit=limit,
        )

        return answer
