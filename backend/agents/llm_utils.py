import json
import logging
import re
import time
from typing import Any
from google import genai
from google.genai import types
from backend.config import settings

logger = logging.getLogger(__name__)

MAX_RETRIES = 5
BASE_BACKOFF_SECONDS = 2.0

JSON_CONFIG = types.GenerateContentConfig(
    response_mime_type="application/json"
)


def _extract_retry_delay(error: Exception) -> float | None:
    """Try to parse 'Please retry in X.Xs' from the error message."""
    error_text = str(error)
    match = re.search(r"retry in\s+([\d.]+)\s*s", error_text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    return None


def _is_rate_limit_error(error: Exception) -> bool:
    """Check if this is a 429 / RESOURCE_EXHAUSTED error."""
    error_text = str(error).lower()
    return "429" in error_text or "resource_exhausted" in error_text or "quota" in error_text


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


def _call_with_retry(client: genai.Client, prompt: str):
    """Call the Gemini API with automatic retry on rate-limit (429) errors."""
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=JSON_CONFIG,
            )
            return response
        except Exception as error:
            last_error = error
            if not _is_rate_limit_error(error):
                logger.exception("LLM API call failed (non-retryable)")
                raise

            # Extract suggested delay or use exponential backoff
            suggested_delay = _extract_retry_delay(error)
            backoff = suggested_delay if suggested_delay else BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
            # Cap at 60 seconds
            backoff = min(backoff, 60.0)

            if attempt < MAX_RETRIES:
                logger.warning(
                    "Rate limited (429) on attempt %d/%d -- waiting %.1fs before retry",
                    attempt, MAX_RETRIES, backoff,
                )
                time.sleep(backoff)
            else:
                logger.error(
                    "Rate limited (429) on attempt %d/%d -- no retries left",
                    attempt, MAX_RETRIES,
                )
    raise last_error


def generate_json(
    client: genai.Client,
    prompt: str,
    list_key: str | None = None,
) -> dict[str, Any]:
    logger.info("LLM request -> model=%s, prompt_length=%d", settings.GEMINI_MODEL, len(prompt))
    logger.debug("LLM prompt (first 300 chars): %s", prompt[:300])

    response = _call_with_retry(client, prompt)

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