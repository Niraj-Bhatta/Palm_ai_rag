
from app.services.embedding_service import EmbeddingService

embedding_service = EmbeddingService()

texts = [
    "Machine learning is a branch of artificial intelligence.",
    "Deep learning uses neural networks.",
    "I enjoy playing football.",
]

embeddings = embedding_service.generate_embeddings(texts)

for index, embedding in enumerate(embeddings):
    print(f"\nText {index + 1}: {texts[index]}")
    print(f"Vector dimensions: {len(embedding)}")
    print(f"First five values: {embedding[:5]}")
