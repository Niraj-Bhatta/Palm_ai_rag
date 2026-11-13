
from typing import Literal

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
)


ChunkingStrategy = Literal["recursive", "token"]


def chunk_text(
    text: str,
    strategy: ChunkingStrategy = "recursive",
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[str]:
    """
    Split extracted document text into smaller chunks.

    Args:
        text: Extracted document text.
        strategy: Chunking strategy to use.
        chunk_size: Maximum chunk size.
        chunk_overlap: Number of overlapping characters or tokens.

    Returns:
        A list of text chunks.
    """

    if not text.strip():
        raise ValueError("Cannot chunk empty text.")

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "Chunk overlap must be non-negative and smaller than chunk size."
        )

    if strategy == "recursive":
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )

    elif strategy == "token":
        splitter = TokenTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            encoding_name="cl100k_base",
        )

    else:
        raise ValueError("Unsupported chunking strategy.")

    chunks = splitter.split_text(text)

    return chunks
