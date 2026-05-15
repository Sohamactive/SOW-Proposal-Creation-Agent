# backend/config.py

import logging
import os
import sys
from dotenv import load_dotenv

load_dotenv()


def _configure_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    root = logging.getLogger()
    root.setLevel(log_level)
    if root.handlers:
        return
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-36s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)
    console.setFormatter(formatter)
    root.addHandler(console)
    for noisy in ("httpx", "httpcore", "urllib3", "grpc", "google.auth"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


_configure_logging()
logger = logging.getLogger(__name__)


class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    GEMINI_TIMEOUT_MS = int(os.getenv("GEMINI_TIMEOUT_MS", "120000"))
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "knowledge_base")
    CORS_ALLOW_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ALLOW_ORIGINS",
            "http://127.0.0.1:8000,http://localhost:8000"
        ).split(",")
        if origin.strip()
    ]
    EMBEDDING_DIMENSION = 768
    CHUNK_SIZE = 400
    CHUNK_OVERLAP = 50
    RETRIEVAL_TOP_K = 3
    EXPORT_FOLDER = os.getenv("EXPORT_FOLDER", "./generated_proposals")
    PROPOSAL_JOB_TIMEOUT_SECONDS = int(os.getenv("PROPOSAL_JOB_TIMEOUT_SECONDS", "600"))


settings = Settings()
logger.info("Settings loaded -- model=%s, qdrant=%s", settings.GEMINI_MODEL, settings.QDRANT_URL)
