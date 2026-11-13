
from typing import Literal
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.db.database import get_db
from app.db.models import Document

from app.services.extraction_service import extract_text
from app.services.chunking_service import chunk_text
from app.services.embedding_service import generate_document_embeddings
from app.services.vector_store_service import get_vector_store


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    chunking_strategy: Literal["recursive", "token"] = Form("recursive"),
    db: Session = Depends(get_db),
) -> dict:

    # 1. Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is missing.",
        )

    # 2. Validate file extension
    allowed_extensions = {".pdf", ".txt"}

    extension = "." + file.filename.rsplit(".", 1)[-1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported.",
        )

    # 3. Read uploaded file
    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    try:
        # 4. Extract document text
        extracted_text = extract_text(
            file_content=file_content,
            filename=file.filename,
        )

        # 5. Split extracted text into chunks
        chunks = chunk_text(
            text=extracted_text,
            strategy=chunking_strategy,
        )

        # 6. Generate embeddings
        embeddings = await run_in_threadpool(
            generate_document_embeddings,
            chunks,
        )

        # 7. Generate unique document ID
        document_id = str(uuid4())

        # 8. Store vectors in Qdrant cloid database
        vector_store = await run_in_threadpool(get_vector_store)

        stored_count = await run_in_threadpool(
            vector_store.store_chunks,
            chunks,
            embeddings,
            document_id,
            file.filename,
            chunking_strategy,
        )

        # 9. Save document metadata in SQLite
        document = Document(
            id=document_id,
            filename=file.filename,
            chunking_strategy=chunking_strategy,
            character_count=len(extracted_text),
            chunk_count=len(chunks),
            embedding_dimensions=len(embeddings[0]) if embeddings else 0,
            status="completed",
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        # 10. Return ingestion result
        return {
            "document_id": document_id,
            "filename": file.filename,
            "message": "Document ingested and stored successfully.",
            "chunking_strategy": chunking_strategy,
            "character_count": len(extracted_text),
            "chunk_count": len(chunks),
            "embedding_count": len(embeddings),
            "embedding_dimensions": len(embeddings[0]) if embeddings else 0,
            "stored_vectors": stored_count,
        }

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed. Please try again.",
        ) from error

    finally:
        await file.close()


@router.get("/")
def list_documents(
    db: Session = Depends(get_db),
) -> list[dict]:

    documents = (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .all()
    )

    return [
        {
            "document_id": document.id,
            "filename": document.filename,
            "chunking_strategy": document.chunking_strategy,
            "character_count": document.character_count,
            "chunk_count": document.chunk_count,
            "embedding_dimensions": document.embedding_dimensions,
            "status": document.status,
            "created_at": document.created_at.isoformat(),
        }
        for document in documents
    ]


@router.get("/{document_id}")
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
) -> dict:

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return {
        "document_id": document.id,
        "filename": document.filename,
        "chunking_strategy": document.chunking_strategy,
        "character_count": document.character_count,
        "chunk_count": document.chunk_count,
        "embedding_dimensions": document.embedding_dimensions,
        "status": document.status,
        "created_at": document.created_at.isoformat(),
    }
