
from fastapi import APIRouter, File, HTTPException, UploadFile
from app.services.extraction_service import extract_text


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
) -> dict[str, str]:

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is missing.",
        )

    allowed_extensions = {".pdf", ".txt"}

    extension = "."+ file.filename.rsplit(".", 1)[-1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported.",
        )

    file_content = await file.read()

    try:
        extracted_text = extract_text(
            file_content=file_content,
            filename = file.filename,
        )

    except  ValueError as error:
        raise HTTPException(
            status_code=400,
            detail = str(error),
        ) from error
    
    return {
        "filename": file.filename,
        "message": "Document text extracted successfully.",
        "character_count": str(len(extracted_text)),
        "extracted_text": extracted_text,
    }
