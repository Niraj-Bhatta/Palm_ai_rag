
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Convert a list of text chunks into numerical vectors.
        """

        if not texts:
            raise ValueError("Cannot generate embeddings for empty text.")

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return embeddings.tolist()

    def generate_query_embedding(
        self,
        query: str,
    ) -> list[float]:
        """
        Generate an embedding for a user query.
        """

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return embedding.tolist()
