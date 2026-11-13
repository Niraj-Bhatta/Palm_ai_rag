
from typing import Literal
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from app.services.extraction_service import extract_text
from app.services.chunking_service import chunk_text
from starlette.concurrency import run_in_threadpool
from app.services.embedding_service import generate_document_embeddings
from uuid import uuid4
from app.services.vector_store_service import get_vector_store


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    chunking_strategy: Literal["recursive", "token"] = Form("recursive"),
) -> dict:

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is missing.",
        )

    allowed_extensions = {".pdf", ".txt"}

    extension = "." + file.filename.rsplit(".", 1)[-1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported.",
        )

    file_content = await file.read()

    try:
        extracted_text = extract_text(
            file_content=file_content,
            filename=file.filename,
        )

        chunks = chunk_text(
            text=extracted_text,
            strategy=chunking_strategy,
        )

        embeddings = await run_in_threadpool(
            generate_document_embeddings,
            chunks,
        )

        document_id = str(uuid4())

        vector_store = await run_in_threadpool(get_vector_store)

        stored_count = await run_in_threadpool(
            vector_store.store_chunks,
            chunks,
            embeddings,
            document_id,
            file.filename,
            chunking_strategy,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


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