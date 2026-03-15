# backend/rag/ingestion.py

import os
from typing import Dict

from backend.document_processing.parser import parse_document
from backend.rag.chunking import chunk_text
from backend.rag.embeddings import generate_document_embeddings
from backend.rag.vector_store import VectorStore
from backend.config import settings
from backend.classification.document_classifier import classify_document


vector_store = VectorStore()


def ingest_document(file_path: str, metadata: Dict):
    """
    Ingest a document into the vector database.

    Pipeline:
    document -> parse -> classify -> chunk -> embeddings -> store
    """

    if metadata.get("source") != "knowledge_base":
        raise ValueError("Only knowledge base documents should be ingested into vector DB")
    # 1. Parse document
    text = parse_document(file_path)

    if not text:
        raise ValueError("Document parsing returned empty text")

    # 2. Classify document
    classification = classify_document(text)

    doc_type = classification.get("doc_type")
    domain = classification.get("domain")
    technologies = classification.get("technologies", [])

    # 3. Chunk document
    chunks = chunk_text(
        text,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )

    if not chunks:
        raise ValueError("Chunking produced no chunks")

    # 4. Generate embeddings
    embeddings = generate_document_embeddings(chunks)

    if not embeddings:
        raise ValueError("Embedding generation failed")

    # 5. Prepare metadata
    base_metadata = metadata.copy()

    base_metadata.update({
        "doc_type": doc_type,
        "domain": domain,
        "technologies": technologies,
        "source_document": os.path.basename(file_path)
    })

    chunk_metadata = []

    for i in range(len(chunks)):
        meta = base_metadata.copy()
        meta["chunk_id"] = i
        chunk_metadata.append(meta)

    # 6. Store in vector DB
    vector_store.add_documents(
        embeddings=embeddings,
        texts=chunks,
        metadata=chunk_metadata
    )

    return {
        "chunks_stored": len(chunks),
        "source_document": base_metadata["source_document"]
    }