import logging
from google import genai
from google.genai import types
from backend.config import settings

logger = logging.getLogger(__name__)


def create_genai_client() -> genai.Client:
    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not set -- LLM calls will fail")
        raise RuntimeError("GEMINI_API_KEY environment variable is not configured")
    logger.info("Creating GenAI client (model=%s, timeout=%dms)", settings.GEMINI_MODEL, settings.GEMINI_TIMEOUT_MS)
    return genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=settings.GEMINI_TIMEOUT_MS),
    )
