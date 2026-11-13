
from typing import Literal

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.extraction_service import extract_text
from app.services.chunking_service import chunk_text

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

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return {
        "filename": file.filename,
        "chunking_strategy": chunking_strategy,
        "character_count": len(extracted_text),
        "chunk_count": len(chunks),
        "chunks": chunks,
    }
