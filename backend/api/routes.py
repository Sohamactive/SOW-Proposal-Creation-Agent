from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
import shutil
import os
from uuid import uuid4

from backend.rag.ingestion import ingest_document
from backend.document_processing.parser import parse_document
from backend.orchestrator.pipeline import ProposalPipeline
from backend.export.proposal_exporter import ProposalExporter
from backend.config import settings

pipeline = ProposalPipeline()
exporter = ProposalExporter()

router = APIRouter()

UPLOAD_FOLDER = "backend/sample_docs"


class ProposalRequest(BaseModel):
    description: str = ""
    project_docs: str = ""


# KNOWLEDGE BASE DOCUMENTS
@router.post("/upload-knowledge-doc")
async def upload_knowledge_doc(file: UploadFile = File(...)):

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    metadata = {
        "source": "knowledge_base"
    }

    result = ingest_document(
        file_path=file_path,
        metadata=metadata
    )

    return {
        "message": "Knowledge document indexed",
        "chunks": result["chunks_stored"]
    }


# PROJECT INPUT DOCUMENTS
@router.post("/upload-project-doc")
async def upload_project_doc(file: UploadFile = File(...)):

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = parse_document(file_path)

    return {
        "message": "Project document processed",
        "text": text[:2000]
    }

@router.post("/generate-proposal")
async def generate_proposal(data: ProposalRequest):

    if not data.description.strip() and not data.project_docs.strip():
        raise HTTPException(status_code=400, detail="Provide a project description or upload a project document")

    result = pipeline.run(
        data.description,
        data.project_docs
    )

    docx_name = f"proposal-{uuid4().hex[:8]}.docx"
    docx_path = exporter.export_docx(result["proposal"], filename=docx_name)

    return {
        "proposal": result["proposal"],
        "review": result["review"],
        "files": {
            "docx_name": docx_name,
            "docx_path": docx_path,
            "docx_download_url": f"/download-proposal/{docx_name}"
        }
    }


@router.get("/download-proposal/{filename}")
async def download_proposal(filename: str):

    safe_name = os.path.basename(filename)
    file_path = os.path.join(settings.EXPORT_FOLDER, safe_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Generated proposal not found")

    return FileResponse(
        path=file_path,
        filename=safe_name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )