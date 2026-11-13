
from app.services.embedding_service import get_embedding_service
from app.services.vector_store_service import get_vector_store


def retrieve_relevant_chunks(
    question: str,
    limit: int = 5,
    document_id: str | None = None,
) -> list[dict]:
    """
    Convert a question into an embedding and retrieve
    relevant document chunks from Qdrant.
    """

    embedding_service = get_embedding_service()

    query_embedding = embedding_service.generate_query_embedding(
        question
    )

    vector_store = get_vector_store()

    results = vector_store.search_chunks(
        query_embedding=query_embedding,
        limit=limit,
        document_id=document_id,
    )

    return results
