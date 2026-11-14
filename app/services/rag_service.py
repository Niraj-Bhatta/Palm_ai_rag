
from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.llm_service import get_llm_service
from app.services.memory_service import (
    get_redis_client,
    ConversationMemory,
)


def answer_question(
    question: str,
    limit: int = 5,
    document_id: str | None = None,
    conversation_id: str = "default",
) -> dict:

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    # 1. Initialize conversation memory.
    redis_client = get_redis_client()
    memory = ConversationMemory(redis_client)

    # 2. Retrieve previous conversation messages.
    history = memory.get_history(
        conversation_id=conversation_id,
        limit=10,
    )

    # 3. Retrieve relevant document chunks.
    retrieved_chunks = retrieve_relevant_chunks(
        question=question,
        limit=limit,
        document_id=document_id,
    )

    if not retrieved_chunks:
        answer = "I couldn't find relevant information in the uploaded documents."

        memory.add_message(conversation_id, "user", question)
        memory.add_message(conversation_id, "assistant", answer)

        return {
            "answer": answer,
            "sources": [],
            "retrieved_count": 0,
        }

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

    # 4. Generate an answer using document context and chat history.
    llm = get_llm_service()

    answer = llm.generate_answer(
        question=question,
        context=context,
        history=history,
    )

    # 5. Save the latest conversation messages.
    memory.add_message(conversation_id, "user", question)
    memory.add_message(conversation_id, "assistant", answer)

    return {
        "answer": answer,
        "sources": sources,
        "retrieved_count": len(retrieved_chunks),
    }
