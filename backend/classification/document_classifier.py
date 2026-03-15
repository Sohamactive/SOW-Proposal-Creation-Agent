# backend/classification/document_classifier.py

import json
from typing import Dict, Any

from google import genai

from backend.config import settings


client = genai.Client(api_key=settings.GEMINI_API_KEY)


CLASSIFICATION_PROMPT = """
Analyze the following project document and classify it.

Return JSON with the following fields:

doc_type:
- rfp
- proposal
- architecture_document
- challenge_spec
- case_study
- requirements_document
- meeting_notes

domain:
- customer_support_ai
- document_intelligence
- crm_automation
- analytics_platform
- fintech_ai
- healthcare_ai
- general_ai_system

technologies:
list of technologies mentioned in the document.

Return JSON only.

Document text:
"""


def classify_document(text: str) -> Dict[str, Any]:
    """
    Classify a document into metadata fields.

    Returns:
        {
            doc_type: str,
            domain: str,
            technologies: List[str]
        }
    """

    prompt = CLASSIFICATION_PROMPT + text[:4000]

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
    )

    raw = response.text.strip() #type: ignore

    try:
        result = json.loads(raw)
    except Exception:
        # fallback if model returns text + JSON
        start = raw.find("{")
        end = raw.rfind("}") + 1
        result = json.loads(raw[start:end])

    return result