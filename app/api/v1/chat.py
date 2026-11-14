import logging

from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import answer_question

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:

    try:
        result = answer_question(
            question=request.question,
            limit=request.limit,
            document_id=request.document_id,
            conversation_id=request.conversation_id,
            db=db,
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