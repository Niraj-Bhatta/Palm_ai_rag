
from app.services.llm_service import get_llm_service


llm = get_llm_service()

context = """
The candidate served as Program Coordinator
at IEEE NCIT Student Branch.

The candidate also served as a Student Branch
Ambassador.
"""

question = "What leadership roles did the candidate hold?"

answer = llm.generate_answer(
    question=question,
    context=context,
)

print("\nGemini Answer:")
print(answer)
