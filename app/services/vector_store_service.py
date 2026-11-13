
import os
from functools import lru_cache
from uuid import uuid4

from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

load_dotenv()


class VectorStoreService:

    def __init__(self) -> None:
        url = os.getenv("QDRANT_URL")
        api_key = os.getenv("QDRANT_API_KEY")

        self.collection_name = os.getenv(
            "QDRANT_COLLECTION",
            "palm_mind_documents",
        )

        if not url or not api_key:
            raise ValueError(
                "QDRANT_URL and QDRANT_API_KEY must be configured."
            )

        self.client = QdrantClient(
            url=url,
            api_key=api_key,
        )

        self.create_collection()
        self.create_payload_indexes()

    def create_collection(self) -> None:
        """Create the collection if it does not already exist."""

        if not self.client.collection_exists(
            collection_name=self.collection_name
        ):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE,
                ),
            )

    def store_chunks(
        self,
        chunks: list[str],
        embeddings: list[list[float]],
        document_id: str,
        filename: str,
        strategy: str,
    ) -> int:
        """Store document chunks and their embeddings in Qdrant."""

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks and embeddings must match."
            )

        points = []

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            points.append(
                models.PointStruct(
                    id=str(uuid4()),
                    vector=embedding,
                    payload={
                        "document_id": document_id,
                        "filename": filename,
                        "chunk_index": index,
                        "text": chunk,
                        "chunking_strategy": strategy,
                    },
                )
            )

        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
                wait=True,
            )

        return len(points)

    def search_chunks(
        self,
        query_embedding: list[float],
        limit: int = 5,
        document_id: str | None = None,
    ) -> list[dict]:
        """Search Qdrant for relevant document chunks."""

        query_filter = None

        if document_id:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=document_id),
                    )
                ]
            )

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        )

        retrieved_chunks = []

        for point in results.points:
            payload = point.payload or {}

            retrieved_chunks.append({
                "text": payload.get("text", ""),
                "document_id": payload.get("document_id"),
                "filename": payload.get("filename"),
                "chunk_index": payload.get("chunk_index"),
                "score": point.score,
            })

        return retrieved_chunks

    def create_payload_indexes(self) -> None:
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="document_id",
            field_schema=models.PayloadSchemaType.KEYWORD,
            wait=True,
        )

@lru_cache(maxsize=1)
def get_vector_store() -> VectorStoreService:
    """Reuse one Qdrant client throughout the application."""
    return VectorStoreService()
