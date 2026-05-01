# backend/rag/embeddings.py

from typing import List, cast
from google.genai import types
from google.genai.types import ContentListUnion
import numpy as np

from backend.config import settings
from backend.genai_client import create_genai_client


# Initialize Gemini client
client = create_genai_client()


def _normalize(vec: List[float]) -> List[float]:
    arr = np.array(vec, dtype=float)
    norm = np.linalg.norm(arr)

    if norm == 0:
        return arr.tolist()

    normalized = arr / norm
    return normalized.astype(float).tolist()


def generate_document_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for document chunks.

    Uses RETRIEVAL_DOCUMENT task type.
    """

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=cast(ContentListUnion, texts),
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=settings.EMBEDDING_DIMENSION
        )
    )

    if not response.embeddings:
        return []

    embeddings = []

    for emb in response.embeddings:
        if emb.values is None:
            continue
        vec = _normalize(emb.values)
        embeddings.append(vec)

    return embeddings


def generate_query_embedding(query: str) -> List[float]:
    """
    Generate embedding for a search query.

    Uses RETRIEVAL_QUERY task type.
    """

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=[query],
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=settings.EMBEDDING_DIMENSION
        )
    )

    if not response.embeddings or response.embeddings[0].values is None:
        raise ValueError("No query embedding returned by Gemini")

    embedding = response.embeddings[0].values

    return _normalize(embedding)
