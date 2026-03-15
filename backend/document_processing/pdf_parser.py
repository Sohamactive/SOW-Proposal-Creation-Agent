# backend/document_processing/pdf_parser.py

from pypdf import PdfReader


def parse_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: Extracted text.
    """

    reader = PdfReader(file_path)
    text_chunks = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_chunks.append(page_text)

    full_text = "\n".join(text_chunks)
    return full_text