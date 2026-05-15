import json
import logging
from typing import Any
from google import genai
from google.genai import types
from backend.config import settings

logger = logging.getLogger(__name__)

JSON_CONFIG = types.GenerateContentConfig(
    response_mime_type="application/json"
)


def _extract_json_payload(raw_text: str) -> str:
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    if not text:
        raise ValueError("Gemini returned an empty response")
    if text[0] in "[{":
        return text
    first_object = text.find("{")
    first_array = text.find("[")
    starts = [index for index in (first_object, first_array) if index != -1]
    if not starts:
        raise ValueError(f"Gemini did not return JSON: {text[:200]}")
    start = min(starts)
    end_object = text.rfind("}")
    end_array = text.rfind("]")
    end = max(end_object, end_array)
    if end < start:
        raise ValueError(f"Gemini returned malformed JSON: {text[:200]}")
    return text[start:end + 1]


def generate_json(
    client: genai.Client,
    prompt: str,
    list_key: str | None = None,
) -> dict[str, Any]:
    logger.info("LLM request -> model=%s, prompt_length=%d", settings.GEMINI_MODEL, len(prompt))
    logger.debug("LLM prompt (first 300 chars): %s", prompt[:300])
    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=JSON_CONFIG,
        )
    except Exception:
        logger.exception("LLM API call failed")
        raise
    raw_text = response.text or ""
    logger.info("LLM response received, length=%d", len(raw_text))
    logger.debug("LLM raw response (first 500 chars): %s", raw_text[:500])
    try:
        payload = json.loads(_extract_json_payload(raw_text))
    except (json.JSONDecodeError, ValueError):
        logger.exception("Failed to parse JSON from LLM response: %s", raw_text[:500])
        raise
    if isinstance(payload, list):
        if list_key is None:
            raise ValueError(f"Expected JSON object from Gemini, received: {type(payload).__name__}")
        logger.info("LLM returned list, wrapping under key=%s (length=%d)", list_key, len(payload))
        return {list_key: payload}
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object from Gemini, received: {type(payload).__name__}")
    logger.info("LLM returned dict with keys: %s", list(payload.keys()))
    return payload