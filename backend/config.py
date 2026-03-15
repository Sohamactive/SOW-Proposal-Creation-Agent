# backend/config.py

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:

    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-2.5-flash"

    # Qdrant
    QDRANT_URL = "http://localhost:6333"
    QDRANT_COLLECTION = "knowledge_base"

    # Embeddings
    EMBEDDING_DIMENSION = 768

    # Chunking
    CHUNK_SIZE = 400
    CHUNK_OVERLAP = 50

    # Retrieval
    RETRIEVAL_TOP_K = 3

    # Export
    EXPORT_FOLDER = "./generated_proposals"


settings = Settings()