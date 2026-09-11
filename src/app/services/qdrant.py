from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.services.embedding import generate_embedding


QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "properties"
VECTOR_SIZE = 384


client = QdrantClient(
    url=QDRANT_URL
)


def create_collection() -> None:
    collections = client.get_collections()

    collection_names = [
        collection.name
        for collection in collections.collections
    ]

    if COLLECTION_NAME not in collection_names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )


def upsert_property(
    property_id: int,
    text: str,
) -> None:
    embedding = generate_embedding(text)

    point = PointStruct(
        id=property_id,
        vector=embedding,
        payload={
            "property_id": property_id,
        },
    )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[point],
    )


def search_properties(
    query: str,
    limit: int = 10,
):
    query_embedding = generate_embedding(query)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit,
    )

    return results.points


def delete_property(
    property_id: int,
) -> None:
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=[property_id],
    )