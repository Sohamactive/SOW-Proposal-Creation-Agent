# backend/config.py

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:

    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Qdrant
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "knowledge_base")

    # CORS
    CORS_ALLOW_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ALLOW_ORIGINS",
            "http://127.0.0.1:8000,http://localhost:8000"
        ).split(",")
        if origin.strip()
    ]

    # Embeddings
    EMBEDDING_DIMENSION = 768

    # Chunking
    CHUNK_SIZE = 400
    CHUNK_OVERLAP = 50

    # Retrieval
    RETRIEVAL_TOP_K = 3

    # Export
    EXPORT_FOLDER = os.getenv("EXPORT_FOLDER", "./generated_proposals")


settings = Settings()