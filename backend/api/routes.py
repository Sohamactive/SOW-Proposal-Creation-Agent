import logging
import os
import shutil
import time
from pathlib import Path
from threading import Event, Lock, Thread
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.config import settings
from backend.document_processing.parser import parse_document
from backend.export.proposal_exporter import ProposalExporter
from backend.orchestrator.pipeline import ProposalPipeline
from backend.rag.ingestion import ingest_document

logger = logging.getLogger(__name__)

pipeline = ProposalPipeline()
exporter = ProposalExporter()
router = APIRouter()

UPLOAD_FOLDER = "backend/sample_docs"
ALLOWED_UPLOAD_EXTENSIONS = {".pdf", ".docx"}
PIPELINE_STEPS = ["Reading documents", "Analyzing requirements", "Generating proposal", "Quality review", "Done"]

jobs: dict[str, dict] = {}
jobs_lock = Lock()


class ProposalRequest(BaseModel):
    description: str = ""
    project_docs: str = ""


def _sanitize_upload_filename(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename")
    safe_name = Path(file.filename).name
    extension = Path(safe_name).suffix.lower()
    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .pdf and .docx files are supported")
    return safe_name


def _pipeline_progress(step_index: int) -> int:
    bounded_index = max(0, min(step_index, len(PIPELINE_STEPS) - 1))
    return int((bounded_index / (len(PIPELINE_STEPS) - 1)) * 100)


def _set_job_state(job_id: str, **updates) -> None:
    with jobs_lock:
        if job_id not in jobs:
            return
        jobs[job_id].update(updates)
        jobs[job_id]["updated_at"] = time.time()


def _create_job(data: ProposalRequest) -> str:
    job_id = uuid4().hex
    with jobs_lock:
        jobs[job_id] = {
            "job_id": job_id, "status": "queued", "step_index": 0,
            "step_label": PIPELINE_STEPS[0], "progress": 0, "error": None,
            "result": None, "created_at": time.time(), "updated_at": time.time(),
            "request": {"description": data.description, "project_docs": data.project_docs},
        }
    logger.info("Job created: %s", job_id)
    return job_id


def _run_generation_job(job_id: str) -> None:
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        logger.error("Job %s not found when worker started", job_id)
        return
    request_data = job.get("request", {})
    description = str(request_data.get("description", "")).strip()
    project_docs = str(request_data.get("project_docs", "")).strip()
    if not description and not project_docs:
        logger.warning("Job %s -- no input provided", job_id)
        _set_job_state(job_id, status="failed", error="Provide a project description or upload a project document", progress=0)
        return
    logger.info("Job %s -- starting generation (desc_len=%d, docs_len=%d)", job_id, len(description), len(project_docs))
    _set_job_state(job_id, status="running", step_index=0, step_label=PIPELINE_STEPS[0], progress=0)
    heartbeat_stop = Event()

    def heartbeat() -> None:
        while not heartbeat_stop.wait(5):
            _set_job_state(job_id)

    heartbeat_thread = Thread(target=heartbeat, daemon=True)
    heartbeat_thread.start()

    def on_progress(step_index: int, step_label: str) -> None:
        logger.info("Job %s -- step %d: %s", job_id, step_index, step_label)
        _set_job_state(job_id, status="running", step_index=step_index, step_label=step_label, progress=_pipeline_progress(step_index))

    try:
        result = pipeline.run(description, project_docs, progress_callback=on_progress)
        docx_name = f"proposal-{uuid4().hex[:8]}.docx"
        exporter.export_docx(result["proposal"], filename=docx_name)
        _set_job_state(
            job_id, status="completed", step_index=4, step_label=PIPELINE_STEPS[4], progress=100, error=None,
            result={"proposal": result["proposal"], "review": result["review"],
                     "files": {"docx_name": docx_name, "docx_download_url": f"/download-proposal/{docx_name}"}},
        )
        logger.info("Job %s -- completed successfully, docx=%s", job_id, docx_name)
    except Exception as error:
        logger.exception("Job %s -- FAILED", job_id)
        _set_job_state(job_id, status="failed", error=str(error) or "Proposal generation failed")
    finally:
        heartbeat_stop.set()


@router.post("/upload-knowledge-doc")
async def upload_knowledge_doc(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    safe_name = _sanitize_upload_filename(file)
    file_path = os.path.join(UPLOAD_FOLDER, safe_name)
    logger.info("Uploading knowledge doc: %s", safe_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    metadata = {"source": "knowledge_base"}
    result = ingest_document(file_path=file_path, metadata=metadata)
    logger.info("Knowledge doc indexed: %s (%d chunks)", safe_name, result["chunks_stored"])
    return {"message": "Knowledge document indexed", "chunks": result["chunks_stored"]}


@router.post("/upload-project-doc")
async def upload_project_doc(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    safe_name = _sanitize_upload_filename(file)
    file_path = os.path.join(UPLOAD_FOLDER, safe_name)
    logger.info("Uploading project doc: %s", safe_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    text = parse_document(file_path)
    logger.info("Project doc parsed: %s (text_length=%d)", safe_name, len(text))
    return {"message": "Project document processed", "text": text[:2000]}


@router.post("/generate-proposal-job")
async def generate_proposal_job(data: ProposalRequest):
    logger.info("POST /generate-proposal-job -- desc_len=%d, docs_len=%d", len(data.description), len(data.project_docs))
    job_id = _create_job(data)
    worker = Thread(target=_run_generation_job, args=(job_id,), daemon=True)
    worker.start()
    return {"job_id": job_id, "status_url": f"/proposal-job/{job_id}"}


@router.get("/proposal-job/{job_id}")
async def get_proposal_job(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] in {"queued", "running"}:
        runtime = time.time() - float(job.get("created_at", time.time()))
        if runtime > settings.PROPOSAL_JOB_TIMEOUT_SECONDS:
            logger.warning("Job %s timed out after %.0fs", job_id, runtime)
            _set_job_state(job_id, status="failed", error=f"Generation timed out after {settings.PROPOSAL_JOB_TIMEOUT_SECONDS}s.")
            with jobs_lock:
                job = jobs.get(job_id)
    return {
        "job_id": job["job_id"], "status": job["status"], "step_index": job["step_index"],
        "step_label": job["step_label"], "progress": job["progress"], "error": job["error"],
        "result": job["result"], "created_at": job.get("created_at"), "updated_at": job.get("updated_at"),
    }


@router.post("/generate-proposal")
async def generate_proposal(data: ProposalRequest):
    logger.info("POST /generate-proposal (sync) -- desc_len=%d", len(data.description))
    if not data.description.strip() and not data.project_docs.strip():
        raise HTTPException(status_code=400, detail="Provide a project description or upload a project document")
    try:
        result = pipeline.run(data.description, data.project_docs)
        docx_name = f"proposal-{uuid4().hex[:8]}.docx"
        exporter.export_docx(result["proposal"], filename=docx_name)
    except Exception as error:
        logger.exception("Sync proposal generation failed")
        raise HTTPException(status_code=500, detail=str(error) or "Proposal generation failed") from error
    return {"proposal": result["proposal"], "review": result["review"],
            "files": {"docx_name": docx_name, "docx_download_url": f"/download-proposal/{docx_name}"}}


@router.get("/download-proposal/{filename}")
async def download_proposal(filename: str):
    safe_name = os.path.basename(filename)
    if Path(safe_name).suffix.lower() != ".docx":
        raise HTTPException(status_code=400, detail="Only .docx downloads are allowed")
    file_path = os.path.join(settings.EXPORT_FOLDER, safe_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Generated proposal not found")
    logger.info("Downloading proposal: %s", safe_name)
    return FileResponse(path=file_path, filename=safe_name,
                        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
