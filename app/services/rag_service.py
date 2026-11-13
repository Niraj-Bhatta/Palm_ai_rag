
from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.llm_service import get_llm_service


def answer_question(
    question: str,
    limit: int = 5,
    document_id: str | None = None,
) -> dict:

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    # Step 1: Retrieve relevant document chunks
    retrieved_chunks = retrieve_relevant_chunks(
        question=question,
        limit=limit,
        document_id=document_id,
    )

    # Step 2: Handle cases where no chunks are retrieved
    if not retrieved_chunks:
        return {
            "answer": "I couldn't find relevant information in the uploaded documents.",
            "sources": [],
            "retrieved_count": 0,
        }

    # Step 3: Format retrieved chunks into context
    context_parts = []
    sources = []

    for chunk in retrieved_chunks:
        filename = chunk.get("filename", "Unknown")
        chunk_index = chunk.get("chunk_index")
        text = chunk.get("text", "")

        context_parts.append(
            f"""
Source: {filename}
Chunk: {chunk_index}
Content:
{text}
"""
        )

        sources.append({
            "filename": filename,
            "document_id": chunk.get("document_id"),
            "chunk_index": chunk_index,
            "score": chunk.get("score"),
        })

    context = "\n---\n".join(context_parts)

    # Step 4: Generate an answer using Gemini
    llm = get_llm_service()

    answer = llm.generate_answer(
        question=question,
        context=context,
    )

    # Step 5: Return answer and source references
    return {
        "answer": answer,
        "sources": sources,
        "retrieved_count": len(retrieved_chunks),
    }
