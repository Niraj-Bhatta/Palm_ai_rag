
from app.services.rag_service import answer_question

question = "What leadership positions and roles has the candidate held?"

result = answer_question(
    question=question,
    limit=5,
)

print("\nQuestion:")
print(question)

print("\nRAG Answer:")
print(result["answer"])

print("\nRetrieved Chunks:")
print(result["retrieved_count"])

print("\nSources:")
for source in result["sources"]:
    print(source)
