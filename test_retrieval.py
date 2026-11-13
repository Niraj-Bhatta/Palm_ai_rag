
from app.services.retrieval_service import retrieve_relevant_chunks


question = "What leadership positions and roles has the candidate held?"
results = retrieve_relevant_chunks(
    question=question,
    limit=3,
)

for index, result in enumerate(results, start=1):
    print(f"\nResult {index}")
    print("Filename:", result["filename"])
    print("Score:", result["score"])
    print("Text:", result["text"][:300])
