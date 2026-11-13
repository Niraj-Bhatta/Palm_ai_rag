import logging

from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import answer_question

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:

    try:
        result = answer_question(
            question=request.question,
            limit=request.limit,
            document_id=request.document_id,
        )

        return ChatResponse(**result)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception("Chat request failed")

        raise HTTPException(
            status_code=500,
            detail="Failed to generate an answer.",
        ) from error