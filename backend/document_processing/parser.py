import os
from .pdf_parser import parse_pdf
from .docx_parser import parse_docx


def parse_document(file_path: str) -> str:
    """
    Detect file type and extract text.

    Supported formats:
    - PDF
    - DOCX
    """

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return parse_pdf(file_path)

    elif ext == ".docx":
        return parse_docx(file_path)

    else:
        raise ValueError(f"Unsupported file type: {ext}")