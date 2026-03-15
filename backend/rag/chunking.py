# backend/rag/chunking.py

from typing import List


def chunk_text(
    text: str,
    chunk_size: int = 400,
    chunk_overlap: int = 50
) -> List[str]:
    """
    Split text into overlapping chunks for RAG.

    Args:
        text (str): Input text.
        chunk_size (int): Number of words per chunk.
        chunk_overlap (int): Overlap between chunks.

    Returns:
        List[str]: List of text chunks.
    """

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk = " ".join(chunk_words)

        chunks.append(chunk)

        start += chunk_size - chunk_overlap

    return chunks