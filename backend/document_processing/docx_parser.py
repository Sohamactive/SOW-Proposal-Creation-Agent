# backend/document_processing/docx_parser.py

from docx import Document


def parse_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file.

    Args:
        file_path (str): Path to DOCX file.

    Returns:
        str: Extracted text.
    """

    document = Document(file_path)
    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            paragraphs.append(text)

    full_text = "\n".join(paragraphs)
    return full_text