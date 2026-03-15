from pathlib import Path
from backend.rag.ingestion import ingest_document

BASE_DIR = Path(__file__).resolve().parent

file_path = BASE_DIR / "sample_docs" / "cover-letter-v1.pdf"

result = ingest_document(
    file_path=str(file_path),
    metadata={
        "doc_type": "proposal",
        "domain": "general",
        "source_document": "cover-letter-v1.pdf"
    }
)

print(result)