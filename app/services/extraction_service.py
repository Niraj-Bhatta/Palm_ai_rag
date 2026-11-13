
import pymupdf


def extract_text(file_content: bytes, filename: str) -> str:
    """
    Extract text from a PDF or TXT document.

    Args:
        file_content: Raw bytes of the uploaded file.
        filename: Original filename.

    Returns:
        Extracted document text.
    """

    extension = filename.rsplit(".", 1)[-1].lower()

    if extension == "pdf":
        try:
            document = pymupdf.open(
                stream=file_content,
                filetype="pdf",
            )

            extracted_pages = []

            for page in document:
                page_text = page.get_text("text")
                extracted_pages.append(page_text)

            document.close()

            text = "\n".join(extracted_pages)

        except Exception as error:
            raise ValueError(
                f"Could not extract PDF text: {error}"
            ) from error

    elif extension == "txt":
        try:
            text = file_content.decode("utf-8-sig")

        except UnicodeDecodeError as error:
            raise ValueError(
                "The TXT file must use UTF-8 encoding."
            ) from error

    else:
        raise ValueError("Unsupported file format.")

    if not text.strip():
        raise ValueError(
            "No extractable text found in the document."
        )

    return text.strip()
