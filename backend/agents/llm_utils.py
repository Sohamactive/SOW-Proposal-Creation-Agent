import json
from typing import Any

from google import genai
from google.genai import types

from backend.config import settings


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
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=JSON_CONFIG,
    )

    payload = json.loads(_extract_json_payload(response.text or ""))

    if isinstance(payload, list):
        if list_key is None:
            raise ValueError(f"Expected JSON object from Gemini, received: {type(payload).__name__}")
        return {list_key: payload}

    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object from Gemini, received: {type(payload).__name__}")

    return payload