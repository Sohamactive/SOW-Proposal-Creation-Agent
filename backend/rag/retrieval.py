# backend/rag/retrieval.py

from typing import List, Optional

from backend.rag.embeddings import generate_query_embedding
from backend.rag.vector_store import VectorStore
from backend.config import settings


vector_store = VectorStore()


def retrieve_chunks(
    query: str,
    top_k: Optional[int] = None,
):
    """
    Retrieve relevant document chunks for a query.
    """

    if top_k is None:
        top_k = settings.RETRIEVAL_TOP_K

    # 1. Generate query embedding
    query_embedding = generate_query_embedding(query)

    # 2. Search vector database
    results = vector_store.search(query_embedding, top_k)

    # 3. Extract payloads
    chunks = []

    for r in results:
        payload = r.payload
        if payload and "text" in payload:
            chunks.append(payload)

    return chunks


def retrieve_context(query: str, top_k: Optional[int] = None) -> str:
    """
    Retrieve relevant chunks and combine them into context text.
    """

    chunks = retrieve_chunks(query, top_k)

    context_parts = []

    for chunk in chunks:
        context_parts.append(chunk["text"])

    context = "\n\n".join(context_parts)

    return context