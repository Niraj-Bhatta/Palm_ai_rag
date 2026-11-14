
from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.llm_service import get_llm_service
from app.services.memory_service import (
    get_redis_client,
    ConversationMemory,
)
from sqlalchemy.orm import Session
from app.services.booking_conversation_service import (
    handle_booking_message,
)

def is_booking_request(
    question: str,
    booking_state: dict | None = None,
) -> bool:
    """Determine whether a message belongs to an interview booking flow."""

    # Continue an existing booking conversation.
    if booking_state and booking_state.get("status") in {
        "collecting",
        "awaiting_confirmation",
    }:
        return True

    booking_phrases = (
        "schedule an interview",
        "schedule my interview",
        "book an interview",
        "book my interview",
        "interview booking",
        "arrange an interview",
        "interview appointment",
        "interview slot",
    )

    normalized_question = question.lower()

    return any(
        phrase in normalized_question
        for phrase in booking_phrases
    )


def answer_question(
    question: str,
    limit: int = 5,
    document_id: str | None = None,
    conversation_id: str = "default",
    db: Session | None = None,
) -> dict:

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if db is None:
        raise ValueError("Database session is required.")

    # 1. Initialize conversation memory.
    redis_client = get_redis_client()
    memory = ConversationMemory(redis_client)

    # 2. Retrieve previous conversation messages.
    history = memory.get_history(
        conversation_id=conversation_id,
        limit=10,
    )
    # Handle interview booking before performing document retrieval.
    booking_state = memory.get_booking_state(conversation_id)

    if is_booking_request(question, booking_state):
        result = handle_booking_message(
            question=question,
            history=history,
            conversation_id=conversation_id,
            memory=memory,
            db=db,
        )

        # Save this conversation turn in Redis.
        memory.add_message(conversation_id, "user", question)
        memory.add_message(
            conversation_id,
            "assistant",
            result["answer"],
        )

        return result



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
